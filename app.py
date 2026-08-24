import streamlit as st
import math
from fpdf import FPDF
from datetime import datetime

# --- INICIALIZAÇÃO DA MEMÓRIA DO SISTEMA ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        'preco_resma': 150.00,
        'custo_garra': 1.50,
        'custo_holler': 1.20,
        'custo_foto': 0.80,
        'custo_bopp': 0.40,
        'custo_caneca': 12.00,
        'custo_insumo_caneca': 1.50,
        'custo_sacola': 0.00,
        'custo_caixinha': 0.00,
        'custo_cartonada': 0.00
    }

# Memória para salvar as compras registradas
if 'compras_realizadas' not in st.session_state:
    st.session_state.compras_realizadas = []

class PrecificadoraGrafica:
    def __init__(self, custo_hora_maquina, imposto_percentual):
        self.custo_hora_maquina = custo_hora_maquina
        self.imposto_percentual = imposto_percentual

    def calcular_aproveitamento(self, larg_mae, alt_mae, larg_peca, alt_peca):
        corte_larg_1 = larg_mae // larg_peca
        corte_alt_1 = alt_mae // alt_peca
        rendimento_1 = corte_larg_1 * corte_alt_1

        corte_larg_2 = larg_mae // alt_peca
        corte_alt_2 = alt_mae // larg_peca
        rendimento_2 = corte_larg_2 * corte_alt_2
        return int(max(rendimento_1, rendimento_2))

    def sugerir_encadernacao(self, qtd_folhas, tipo_garra):
        if "Espiral" in tipo_garra:
            if qtd_folhas <= 25: return "Espiral 07mm"
            if qtd_folhas <= 50: return "Espiral 09mm"
            if qtd_folhas <= 70: return "Espiral 12mm"
            if qtd_folhas <= 85: return "Espiral 14mm"
            if qtd_folhas <= 100: return "Espiral 17mm"
            if qtd_folhas <= 120: return "Espiral 20mm"
            if qtd_folhas <= 140: return "Espiral 23mm"
            if qtd_folhas <= 160: return "Espiral 25mm"
            if qtd_folhas <= 200: return "Espiral 29mm"
            if qtd_folhas <= 250: return "Espiral 33mm"
            if qtd_folhas <= 350: return "Espiral 40mm"
            if qtd_folhas <= 400: return "Espiral 45mm"
            return "Espiral 50mm"
        else:
            if qtd_folhas <= 120: return "Wire-o 5/8\" (15,8 mm)"
            if qtd_folhas <= 140: return "Wire-o 3/4\" (19,0 mm)"
            if qtd_folhas <= 180: return "Wire-o 7/8\" (22,2 mm)"
            if qtd_folhas <= 200: return "Wire-o 1\" (25,4 mm)"
            if qtd_folhas <= 250: return "Wire-o 1 1/8\" (28,5 mm)"
            return "Wire-o 1 1/4\" (31,7 mm) ou maior"

    def calcular_orcamento_papel(self, preco_resma, folhas_por_resma, total_folhas_mae, tempo_total_min, custo_acab, custo_encadernacao, custo_capa, margem):
        custo_mat = (preco_resma / folhas_por_resma) * total_folhas_mae if total_folhas_mae > 0 else 0
        custo_maq = (tempo_total_min / 60.0) * self.custo_hora_maquina
        
        custo_total_producao = custo_mat + custo_maq + custo_acab + custo_encadernacao + custo_capa

        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        preco_venda = custo_total_producao / fator_divisor
        
        return {
            "Custo do Papel (Miolo)": custo_mat,
            "Custo Capa Dura (Holler/Foto/BOPP)": custo_capa,
            "Custo Insumos (Garra/Encadernação)": custo_encadernacao,
            "Custo de Máquina / Energia / Mão de Obra": custo_maq,
            "Acabamentos Extras": custo_acab,
            "Custo Total de Produção": custo_total_producao,
            "Valor do Imposto": preco_venda * (self.imposto_percentual / 100.0),
            "Lucro Estimado": preco_venda * (margem / 100.0),
            "Preço de Venda Final": preco_venda,
            "Preço Unitário": 0
        }

    def calcular_orcamento_sublimacao(self, custo_caneca, custo_insumos, custo_embalagem_unit, tempo_prensa_min, tiragem, margem):
        custo_mat_caneca = custo_caneca * tiragem
        custo_mat_insumo = custo_insumos * tiragem
        custo_mat_embalagem = custo_embalagem_unit * tiragem
        
        tempo_total_min = (tempo_prensa_min * tiragem) + 5 
        custo_maq = (tempo_total_min / 60.0) * self.custo_hora_maquina
        
        custo_total_producao = custo_mat_caneca + custo_mat_insumo + custo_mat_embalagem + custo_maq
        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        preco_venda = custo_total_producao / fator_divisor
        
        return {
            "Custo Canecas Brancas": custo_mat_caneca,
            "Custo Insumos (Papel/Tinta)": custo_mat_insumo,
            "Custo Embalagens (Caixas/Sacolas)": custo_mat_embalagem,
            "Custo de Máquina (Prensa)": custo_maq,
            "Custo Total de Produção": custo_total_producao,
            "Valor do Imposto": preco_venda * (self.imposto_percentual / 100.0),
            "Lucro Estimado": preco_venda * (margem / 100.0),
            "Preço de Venda Final": preco_venda,
            "Preço Unitário": 0
        }

def gerar_pdf(resultado, qtd_pecas, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Orcamento Grafico", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhes do Pedido:", ln=True)
    pdf.set_font("Arial", '', 12)
    
    if nome_cliente:
        pdf.cell(200, 8, txt=f"Cliente: {nome_cliente}", ln=True)
        
    pdf.cell(200, 8, txt=f"Tiragem Total: {qtd_pecas} unidades", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resumo Financeiro:", ln=True)
    pdf.set_font("Arial", '', 12)
    
    for chave, valor in resultado.items():
        if chave == "Preço de Venda Final":
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(140, 10, txt=str(chave).upper(), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
        elif chave != "Preço Unitário" and valor > 0:
            pdf.set_font("Arial", '', 12)
            pdf.cell(140, 10, txt=str(chave), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
            
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Orcamento gerado automaticamente. Validade de 15 dias.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- CONFIGURAÇÃO DA PÁGINA E INTERFACE ---
st.set_page_config(page_title="Orçamento Gráfico Premium", layout="wide")
st.title("🖨️ Sistema de Precificação Gráfica")

aba_orcamento, aba_compras = st.tabs(["🖨️ Fazer Orçamento", "📦 Controle de Compras"])

st.sidebar.header("Configurações Fixas")
custo_hora_maq = st.sidebar.number_input("Custo Hora/Máquina (R$)", value=45.00, step=5.00)
imposto_perc = st.sidebar.number_input("Imposto (%)", value=10.00, step=1.00)
sistema = PrecificadoraGrafica(custo_hora_maq, imposto_perc)

# ==========================================
# ABA 2: CONTROLE DE COMPRAS E GASTOS (NOVO)
# ==========================================
with aba_compras:
    st.header("🛒 Lançamento de Compras de Materiais")
    st.write("Registre aqui tudo o que você comprar para a gráfica. O sistema guardará o seu histórico de gastos.")
    
    # Formulário para lançar uma nova compra
    with st.form("form_nova_compra", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c1:
            data_compra = st.date_input("Data da Compra", value=datetime.today())
        with col_c2:
            item_comprado = st.text_input("Material Comprado (Ex: 100 Placas de Holler, 10 Canecas)")
        with col_c3:
            valor_pago = st.number_input("Valor Total Pago (R$)", min_value=0.0, step=10.00)
            
        btn_registrar = st.form_submit_button("Registrar Gasto")
        
        if btn_registrar:
            if item_comprado == "":
                st.warning("Por favor, digite o nome do material comprado.")
            else:
                st.session_state.compras_realizadas.append({
                    "Data": data_compra.strftime("%d/%m/%Y"),
                    "Material": item_comprado,
                    "Total Pago (R$)": valor_pago
                })
                st.success(f"Compra de '{item_comprado}' registrada com sucesso!")

    # Exibição do Histórico e Total Gasto
    if len(st.session_state.compras_realizadas) > 0:
        st.markdown("---")
        st.subheader("📋 Seu Histórico de Gastos")
        
        total_investido = sum(compra["Total Pago (R$)"] for compra in st.session_state.compras_realizadas)
        st.metric(label="Total Gasto Acumulado", value=f"R$ {total_investido:.2f}")
        
        # Cria uma tabela bonita com os dados
        st.dataframe(st.session_state.compras_realizadas, use_container_width=True)
    else:
        st.info("Nenhuma compra registrada ainda. Adicione os seus primeiros gastos acima!")

    # Escondendo a configuração de preços base em um expansor para manter a tela limpa
    st.markdown("---")
    with st.expander("⚙️ Atualizar Preços Padrão para Orçamentos (Opcional)", expanded=False):
        st.write("Atualize os valores unitários abaixo apenas se quiser que eles mudem automaticamente na hora de fazer novos orçamentos.")
        col_est1, col_est2, col_est3 = st.columns(3)
        with col_est1:
            st.session_state.estoque['preco_resma'] = st.number_input("Preço da Resma A4 (R$)", value=st.session_state.estoque['preco_resma'], step=5.00)
            st.session_state.estoque['custo_caneca'] = st.number_input("Caneca Branca (unid) (R$)", value=st.session_state.estoque['custo_caneca'], step=0.50)
            st.session_state.estoque['custo_insumo_caneca'] = st.number_input("Tinta/Papel Sublimático (R$)", value=st.session_state.estoque['custo_insumo_caneca'], step=0.10)
        with col_est2:
            st.session_state.estoque['custo_garra'] = st.number_input("Espiral/Wire-o (R$)", value=st.session_state.estoque['custo_garra'], step=0.10)
            st.session_state.estoque['custo_holler'] = st.number_input("Papelão Holler (unid) (R$)", value=st.session_state.estoque['custo_holler'], step=0.10)
            st.session_state.estoque['custo_foto'] = st.number_input("Papel Fotográfico (unid) (R$)", value=st.session_state.estoque['custo_foto'], step=0.10)
            st.session_state.estoque['custo_bopp'] = st.number_input("Laminação BOPP (unid) (R$)", value=st.session_state.estoque['custo_bopp'], step=0.10)
        with col_est3:
            st.session_state.estoque['custo_sacola'] = st.number_input("Sacola Simples (R$)", value=st.session_state.estoque['custo_sacola'], step=0.10)
            st.session_state.estoque['custo_caixinha'] = st.number_input("Caixinha Padrão (R$)", value=st.session_state.estoque['custo_caixinha'], step=0.10)
            st.session_state.estoque['custo_cartonada'] = st.number_input("Caixa Cartonada (R$)", value=st.session_state.estoque['custo_cartonada'], step=0.50)


# ==========================================
# ABA 1: FAZER ORÇAMENTO
# ==========================================
with aba_orcamento:
    st.header("👤 Dados do Cliente")
    nome_cliente = st.text_input("Nome do Cliente / Empresa", placeholder="Digite o nome para sair no PDF...")
    st.markdown("---")

    tipo_produto = st.radio("O que vamos orçar?", [
        "📄 Material Plano (Panfletos, Cartões)", 
        "📔 Material Encadernado (Agendas, Cadernos)",
        "☕ Canecas Sublimáticas (Porcelana)"
    ])

    if tipo_produto == "☕ Canecas Sublimáticas (Porcelana)":
        st.markdown("---")
        st.header("☕ Custos de Sublimação")
        colA, colB, colC = st.columns(3)
        
        with colA:
            custo_caneca = st.number_input("Custo da Caneca Branca (R$)", value=st.session_state.estoque['custo_caneca'], step=1.00)
            custo_insumos = st.number_input("Papel + Tinta por Caneca (R$)", value=st.session_state.estoque['custo_insumo_caneca'], step=0.10)
        with colB:
            tempo_prensa = st.number_input("Tempo de Prensa (min/caneca)", value=3.0, step=0.5)
            tiragem_cliente = st.number_input("Quantidade de Canecas", value=1, step=1)
        with colC:
            margem_lucro = st.number_input("Margem de Lucro Desejada (%)", value=50.00, step=5.00)
            
        st.markdown("---")
        st.header("📦 Embalagens (Opcional)")
        col_emb1, col_emb2, col_emb3 = st.columns(3)
        
        with col_emb1:
            custo_sacola = st.number_input("Custo da Sacola Simples (R$)", value=st.session_state.estoque['custo_sacola'], step=0.50)
        with col_emb2:
            custo_caixinha = st.number_input("Custo da Caixinha Padrão (R$)", value=st.session_state.estoque['custo_caixinha'], step=0.50)
        with col_emb3:
            custo_cartonada = st.number_input("Custo da Caixa Cartonada (R$)", value=st.session_state.estoque['custo_cartonada'], step=1.00)
            
        custo_embalagem_unit = custo_sacola + custo_caixinha + custo_cartonada
            
        st.markdown("---")
        if st.button("Calcular Orçamento", type="primary", use_container_width=True):
            res = sistema.calcular_orcamento_sublimacao(
                custo_caneca, custo_insumos, custo_embalagem_unit, tempo_prensa, tiragem_cliente, margem_lucro
            )
            res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
            
            st.success("Orçamento gerado com sucesso!")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
            r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
            r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
            r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
            
            st.write("### Resumo Detalhado")
            st.json({k: f"R$ {v:.2f}" for k, v in res.items() if v > 0 or k == "Preço Unitário"})
            
            pdf_bytes = gerar_pdf(res, tiragem_cliente, nome_cliente)
            nome_arquivo = f"Orcamento_{nome_cliente.replace(' ', '_')}.pdf" if nome_cliente else "Orcamento_Canecas.pdf"
            st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name=nome_arquivo, mime="application/pdf")

    else:
        mostrar_papel = True
        custo_encadernacao_total = 0.0
        custo_capa_dura_total = 0.0
        tempo_extra_min = 0.0
        
        if tipo_produto == "📔 Material Encadernado (Agendas, Cadernos)":
            st.markdown("---")
            st.header("📖 Configuração do Miolo e Furação")
            
            col_tipo1, col_tipo2 = st.columns(2)
            with col_tipo1:
                modo_servico = st.radio("O serviço inclui impressão do miolo?", ["Sim, Com Impressão", "Não, Apenas Encadernar (Sem Impressão)"])
                if modo_servico == "Não, Apenas Encadernar (Sem Impressão)":
                    mostrar_papel = False
            with col_tipo2:
                tipo_garra = st.radio("Tipo de acabamento:", ["Wire-o (Metal)", "Espiral (Plástico)"])

            col_ag1, col_ag2 = st.columns(2)
            with col_ag1:
                paginas_miolo = st.number_input("Quantas páginas tem o miolo?", value=200, step=10)
                folhas_por_unidade = math.ceil(paginas_miolo / 2)
                st.write(f"Total: **{folhas_por_unidade} folhas** por unidade.")
            with col_ag2:
                st.success(f"💡 **Tamanho Sugerido:** {sistema.sugerir_encadernacao(folhas_por_unidade, tipo_garra)}")
                custo_unit_encadernacao = st.number_input(f"Custo do Insumo ({tipo_garra}) R$", value=st.session_state.estoque['custo_garra'], step=0.10)
                tempo_furacao_unit = st.number_input("Tempo p/ furar e fechar 1 unid (min)", value=3.0, step=0.5)

            st.markdown("---")
            st.header("📓 Composição da Capa Dura")
            usar_capa_dura = st.checkbox("Incluir custos de Capa Dura", value=True)
            
            if usar_capa_dura:
                col_capa1, col_capa2, col_capa3, col_capa4 = st.columns(4)
                with col_capa1:
                    custo_holler = st.number_input("Holler (unid) R$", value=st.session_state.estoque['custo_holler'], step=0.10)
                with col_capa2:
                    custo_foto = st.number_input("Fotográfico (unid) R$", value=st.session_state.estoque['custo_foto'], step=0.10)
                with col_capa3:
                    custo_bopp = st.number_input("BOPP (unid) R$", value=st.session_state.estoque['custo_bopp'], step=0.10)
                with col_capa4:
                    tempo_lam_unit = st.number_input("Tempo Laminação (min)", value=1.5, step=0.5)
                
                custo_capa_unit = custo_holler + custo_foto + custo_bopp
                st.info(f"Custo de material da capa por unidade: **R$ {custo_capa_unit:.2f}**")
            else:
                custo_capa_unit = 0.0
                tempo_lam_unit = 0.0

        st.markdown("---")
        st.header("2. Aproveitamento e Custos Base")
        colA, colB, colC = st.columns(3)
        if mostrar_papel:
            with colA:
                larg_mae = st.number_input("Largura Mãe (cm)", value=66.0)
                alt_mae = st.number_input("Altura Mãe (cm)", value=96.0)
            with colB:
                larg_peca = st.number_input("Largura Final (cm)", value=15.0)
                alt_peca = st.number_input("Altura Final (cm)", value=21.0)
            with colC:
                tiragem_cliente = st.number_input("Tiragem (Unidades)", value=100, step=10)
                perda_folhas = st.number_input("Perda (folhas)", value=20, step=5)

            rendimento = sistema.calcular_aproveitamento(larg_mae, alt_mae, larg_peca, alt_peca)
            st.info(f"**Rendimento:** Cabem {rendimento} peças por folha mãe.")
        else:
            with colA:
                tiragem_cliente = st.number_input("Tiragem (Quantas unidades encadernar?)", value=50, step=5)
            rendimento = 1 

        total_folhas_usadas = 0
        if tipo_produto == "📔 Material Encadernado (Agendas, Cadernos)":
            custo_encadernacao_total = custo_unit_encadernacao * tiragem_cliente
            custo_capa_dura_total = custo_capa_unit * tiragem_cliente
            tempo_extra_min = (tempo_furacao_unit + tempo_lam_unit) * tiragem_cliente
            
            if mostrar_papel and rendimento > 0:
                folhas_mae_por_agenda = folhas_por_unidade / rendimento
                total_folhas_usadas = math.ceil(folhas_mae_por_agenda * tiragem_cliente) + perda_folhas
        else:
            if mostrar_papel and rendimento > 0:
                total_folhas_usadas = math.ceil(tiragem_cliente / rendimento) + perda_folhas

        st.markdown("---")
        st.header("3. Produção e Financeiro")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if mostrar_papel:
                preco_resma = st.number_input("Preço da Resma (R$)", value=st.session_state.estoque['preco_resma'], step=10.00)
                folhas_resma = st.number_input("Folhas por Resma", value=500, step=50)
                st.write(f"📦 Folhas Utilizadas: **{total_folhas_usadas}**")
            else:
                st.info("Serviço sem impressão. Custo de papel é zero.")
                preco_resma = 0
                folhas_resma = 1

        with col2:
            if mostrar_papel:
                setup_min = st.number_input("Tempo Setup Máquina (min)", value=15, step=5)
                tiragem_min = st.number_input("Tempo de Impressão (min)", value=30, step=5)
            else:
                setup_min = 0
                tiragem_min = 0
                st.write(f"⚙️ Mão de Obra Total (Furação + Capa): **{tempo_extra_min} min**")
                
            custo_acab = st.number_input("Outros Acabamentos Extras (R$)", value=0.00)

        with col3:
            margem_lucro = st.number_input("Margem de Lucro (%)", value=40.00, step=5.00)

        st.markdown("---")
        if st.button("Calcular Orçamento", type="primary", use_container_width=True):
            if mostrar_papel and rendimento == 0:
                st.error("Erro: A peça final é maior que a folha mãe.")
            else:
                tempo_total_producao = setup_min + tiragem_min + tempo_extra_min
                res = sistema.calcular_orcamento_papel(
                    preco_resma, folhas_resma, total_folhas_usadas, tempo_total_producao, 
                    custo_acab, custo_encadernacao_total, custo_capa_dura_total, margem_lucro
                )
                res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
                
                st.success("Orçamento gerado com sucesso!")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
                r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
                r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
                r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
                
                st.write("### Resumo Detalhado")
                st.json({k: f"R$ {v:.2f}" for k, v in res.items() if v > 0 or k == "Preço Unitário"})
                
                pdf_bytes = gerar_pdf(res, tiragem_cliente, nome_cliente)
                nome_arquivo = f"Orcamento_{nome_cliente.replace(' ', '_')}.pdf" if nome_cliente else "Orcamento_Grafica.pdf"
                st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name=nome_arquivo, mime="application/pdf")
