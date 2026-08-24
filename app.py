import streamlit as st
import math
from fpdf import FPDF

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

    def calcular_orcamento_papel(self, preco_resma, folhas_por_resma, total_folhas_mae, tempo_total_min, custo_acab, custo_encadernacao, margem):
        custo_mat = (preco_resma / folhas_por_resma) * total_folhas_mae if total_folhas_mae > 0 else 0
        custo_maq = (tempo_total_min / 60.0) * self.custo_hora_maquina
        custo_total_producao = custo_mat + custo_maq + custo_acab + custo_encadernacao

        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        preco_venda = custo_total_producao / fator_divisor
        
        return {
            "Custo do Papel": custo_mat,
            "Custo de Máquina": custo_maq,
            "Acabamentos Extras": custo_acab,
            "Custo Encadernação (Wire-o/Espiral)": custo_encadernacao,
            "Custo Total de Produção": custo_total_producao,
            "Valor do Imposto": preco_venda * (self.imposto_percentual / 100.0),
            "Lucro Estimado": preco_venda * (margem / 100.0),
            "Preço de Venda Final": preco_venda,
            "Preço Unitário": 0
        }

    def calcular_orcamento_sublimacao(self, custo_caneca, custo_insumos, tempo_prensa_min, tiragem, margem):
        custo_mat_caneca = custo_caneca * tiragem
        custo_mat_insumo = custo_insumos * tiragem
        tempo_total_min = (tempo_prensa_min * tiragem) + 5 
        custo_maq = (tempo_total_min / 60.0) * self.custo_hora_maquina
        
        custo_total_producao = custo_mat_caneca + custo_mat_insumo + custo_maq
        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        preco_venda = custo_total_producao / fator_divisor
        
        return {
            "Custo Canecas Brancas": custo_mat_caneca,
            "Custo Insumos (Papel/Tinta)": custo_mat_insumo,
            "Custo de Máquina (Prensa)": custo_maq,
            "Custo Total de Produção": custo_total_producao,
            "Valor do Imposto": preco_venda * (self.imposto_percentual / 100.0),
            "Lucro Estimado": preco_venda * (margem / 100.0),
            "Preço de Venda Final": preco_venda,
            "Preço Unitário": 0
        }

def gerar_pdf(resultado, qtd_pecas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Orcamento Grafico", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhes do Pedido:", ln=True)
    pdf.set_font("Arial", '', 12)
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
        elif chave != "Preço Unitário":
            pdf.set_font("Arial", '', 12)
            pdf.cell(140, 10, txt=str(chave), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
            
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Orcamento gerado automaticamente. Validade de 15 dias.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE VISUAL (STREAMLIT) ---
st.set_page_config(page_title="Orçamento Gráfico Premium", layout="wide")
st.title("🖨️ Sistema de Precificação Gráfica")

st.sidebar.header("Configurações Fixas")
custo_hora_maq = st.sidebar.number_input("Custo Hora/Máquina (R$)", value=45.00, step=5.00)
imposto_perc = st.sidebar.number_input("Imposto (%)", value=10.00, step=1.00)
sistema = PrecificadoraGrafica(custo_hora_maq, imposto_perc)

tipo_produto = st.radio("O que vamos orçar?", [
    "📄 Material Plano (Panfletos, Cartões)", 
    "📔 Material Encadernado (Agendas, Cadernos)",
    "☕ Canecas Sublimáticas (Porcelana)"
])

# ==========================================
# LÓGICA PARA CANECAS DE SUBLIMAÇÃO
# ==========================================
if tipo_produto == "☕ Canecas Sublimáticas (Porcelana)":
    st.markdown("---")
    st.header("☕ Custos de Sublimação")
    colA, colB, colC = st.columns(3)
    
    with colA:
        custo_caneca = st.number_input("Custo da Caneca Branca (R$)", value=12.00, step=1.00)
        custo_insumos = st.number_input("Papel + Tinta por Caneca (R$)", value=1.50, step=0.10)
    with colB:
        tempo_prensa = st.number_input("Tempo de Prensa (min/caneca)", value=3.0, step=0.5)
        tiragem_cliente = st.number_input("Quantidade de Canecas", value=10, step=1)
    with colC:
        margem_lucro = st.number_input("Margem de Lucro Desejada (%)", value=50.00, step=5.00)
        
    st.markdown("---")
    if st.button("Calcular Orçamento de Canecas", type="primary", use_container_width=True):
        res = sistema.calcular_orcamento_sublimacao(custo_caneca, custo_insumos, tempo_prensa, tiragem_cliente, margem_lucro)
        res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
        
        st.success("Orçamento gerado com sucesso!")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
        r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
        r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
        r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
        
        st.write("### Resumo Detalhado")
        st.json({k: f"R$ {v:.2f}" for k, v in res.items()})
        
        pdf_bytes = gerar_pdf(res, tiragem_cliente)
        st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name="Orcamento_Canecas.pdf", mime="application/pdf")

# ==========================================
# LÓGICA PARA IMPRESSOS E ENCADERNADOS
# ==========================================
else:
    mostrar_papel = True
    custo_encadernacao_total = 0.0
    tempo_extra_min = 0.0
    
    if tipo_produto == "📔 Material Encadernado (Agendas, Cadernos)":
        st.markdown("---")
        st.header("📖 Configuração da Encadernação")
        
        col_tipo1, col_tipo2 = st.columns(2)
        with col_tipo1:
            modo_servico = st.radio("O serviço inclui impressão do miolo?", ["Sim, Com Impressão", "Não, Apenas Encadernar (Sem Impressão)"])
            if modo_servico == "Não, Apenas Encadernar (Sem Impressão)":
                mostrar_papel = False
        with col_tipo2:
            tipo_garra = st.radio("Tipo de acabamento:", ["Wire-o (Metal)", "Espiral (Plástico)"])

        st.markdown("---")
        col_ag1, col_ag2 = st.columns(2)
        
        with col_ag1:
            paginas_miolo = st.number_input("Quantas páginas tem o material?", value=200, step=10)
            folhas_por_unidade = math.ceil(paginas_miolo / 2)
            st.write(f"Total: **{folhas_por_unidade} folhas** por unidade.")
            
        with col_ag2:
            st.success(f"💡 **Tamanho Sugerido:** {sistema.sugerir_encadernacao(folhas_por_unidade, tipo_garra)}")
            custo_unit_encadernacao = st.number_input(f"Custo Unitário ({tipo_garra} + Capas) R$", value=3.50, step=0.50)
            tempo_furacao_unit = st.number_input("Tempo p/ furar e fechar 1 unidade (min)", value=3.0, step=0.5)

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
        tempo_extra_min = tempo_furacao_unit * tiragem_cliente
        
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
            preco_resma = st.number_input("Preço da Resma (R$)", value=150.00, step=10.00)
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
            st.write(f"⚙️ Mão de Obra: **{tempo_extra_min} min**")
            
        custo_acab = st.number_input("Outros Acabamentos (R$)", value=0.00)

    with col3:
        margem_lucro = st.number_input("Margem de Lucro (%)", value=40.00, step=5.00)

    st.markdown("---")
    if st.button("Calcular Orçamento Completo", type="primary", use_container_width=True):
        if mostrar_papel and rendimento == 0:
            st.error("Erro: A peça final é maior que a folha mãe.")
        else:
            tempo_total_producao = setup_min + tiragem_min + tempo_extra_min
            res = sistema.calcular_orcamento_papel(preco_resma, folhas_resma, total_folhas_usadas, tempo_total_producao, custo_acab, custo_encadernacao_total, margem_lucro)
            res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
            
            st.success("Orçamento gerado com sucesso!")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
            r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
            r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
            r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
            
            st.write("### Resumo Detalhado")
            st.json({k: f"R$ {v:.2f}" for k, v in res.items()})
            
            pdf_bytes = gerar_pdf(res, tiragem_cliente)
            st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name="Orcamento_Grafica.pdf", mime="application/pdf")
