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

    def sugerir_encadernacao(self, qtd_folhas):
        if qtd_folhas <= 50: return "Espiral 9mm  |  Wire-o 3/8\" (Passo 3:1)"
        if qtd_folhas <= 100: return "Espiral 17mm |  Wire-o 5/8\" (Passo 2:1)"
        if qtd_folhas <= 120: return "Espiral 20mm |  Wire-o 3/4\" (Passo 2:1)"
        if qtd_folhas <= 200: return "Espiral 29mm |  Wire-o 1\" (Passo 2:1)"
        return "Espiral 33mm+ | Wire-o 1 1/4\" (Passo 2:1)"

    def calcular_orcamento_papel(self, preco_resma, folhas_por_resma, total_folhas_mae, setup_min, tiragem_min, custo_acab, custo_encadernacao, margem):
        custo_mat = (preco_resma / folhas_por_resma) * total_folhas_mae if total_folhas_mae > 0 else 0
        custo_maq = ((setup_min + tiragem_min) / 60.0) * self.custo_hora_maquina
        custo_total_producao = custo_mat + custo_maq + custo_acab + custo_encadernacao

        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        preco_venda = custo_total_producao / fator_divisor
        
        return {
            "Custo do Papel": custo_mat,
            "Custo de Máquina": custo_maq,
            "Acabamentos Extras": custo_acab,
            "Custo Encadernação": custo_encadernacao,
            "Custo Total de Produção": custo_total_producao,
            "Valor do Imposto": preco_venda * (self.imposto_percentual / 100.0),
            "Lucro Estimado": preco_venda * (margem / 100.0),
            "Preço de Venda Final": preco_venda,
            "Preço Unitário": 0
        }

    def calcular_orcamento_sublimacao(self, custo_caneca, custo_insumos, tempo_prensa_min, tiragem, margem):
        custo_mat_caneca = custo_caneca * tiragem
        custo_mat_insumo = custo_insumos * tiragem
        # Soma o tempo de todas as canecas + 5 min de setup para aquecer a prensa
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
        
        pdf_bytes = gerar_pdf(res, tiragem_cliente)
        st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name="Orcamento_Canecas.pdf", mime="application/pdf")

# ==========================================
# LÓGICA PARA IMPRESSOS E ENCADERNADOS
# ==========================================
else:
    st.header("1. Aproveitamento de Corte")
    colA, colB, colC = st.columns(3)
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

    custo_encadernacao_total = 0.0
    total_folhas_usadas = 0

    if tipo_produto == "📔 Material Encadernado (Agendas, Cadernos)":
        st.markdown("---")
        st.header("📖 Configuração do Miolo e Encadernação")
        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            paginas_miolo = st.number_input("Páginas da agenda", value=200, step=10)
            folhas_por_unidade = math.ceil(paginas_miolo / 2)
            if rendimento > 0:
                folhas_mae_por_agenda = folhas_por_unidade / rendimento
                total_folhas_usadas = math.ceil(folhas_mae_por_agenda * tiragem_cliente) + perda_folhas
        with col_ag2:
            st.success(f"💡 **Sugestão:** {sistema.sugerir_encadernacao(folhas_por_unidade)}")
            custo_unit_encadernacao = st.number_input("Custo Wire-o/Espiral (R$)", value=1.50)
            custo_encadernacao_total = custo_unit_encadernacao * tiragem_cliente
    else:
        if rendimento > 0:
            total_folhas_usadas = math.ceil(tiragem_cliente / rendimento) + perda_folhas

    st.markdown("---")
    st.header("2. Custos Base e Produção")
    col1, col2, col3 = st.columns(3)
    with col1:
        preco_resma = st.number_input("Preço da Resma (R$)", value=150.00, step=10.00)
        folhas_resma = st.number_input("Folhas por Resma", value=500, step=50)
    with col2:
        setup_min = st.number_input("Tempo de Setup (min)", value=15, step=5)
        tiragem_min = st.number_input("Tempo de Tiragem (min)", value=30, step=5)
        custo_acab = st.number_input("Acabamentos (R$)", value=20.00)
    with col3:
        margem_lucro = st.number_input("Margem de Lucro (%)", value=40.00, step=5.00)

    st.markdown("---")
    if st.button("Calcular Orçamento Completo", type="primary", use_container_width=True):
        if rendimento == 0:
            st.error("Erro: Peça maior que a folha mãe.")
        else:
            res = sistema.calcular_orcamento_papel(preco_resma, folhas_resma, total_folhas_usadas, setup_min, tiragem_min, custo_acab, custo_encadernacao_total, margem_lucro)
            res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
            
            st.success("Orçamento gerado com sucesso!")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
            r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
            r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
            r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
            
            pdf_bytes = gerar_pdf(res, tiragem_cliente)
            st.download_button("📄 Baixar Orçamento em PDF", data=pdf_bytes, file_name="Orcamento_Grafica.pdf", mime="application/pdf")
