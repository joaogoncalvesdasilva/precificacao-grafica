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

    def calcular_papel(self, preco_resma, folhas_por_resma, quantidade_folhas):
        custo_por_folha = preco_resma / folhas_por_resma
        return custo_por_folha * quantidade_folhas

    def calcular_producao(self, tempo_setup_minutos, tempo_tiragem_minutos):
        tempo_total_horas = (tempo_setup_minutos + tempo_tiragem_minutos) / 60.0
        return tempo_total_horas * self.custo_hora_maquina

    def calcular_orcamento(
        self, preco_resma, folhas_por_resma, qtd_folhas_usadas,
        setup_min, tiragem_min, custo_acabamento, margem_lucro_desejada
    ):
        custo_mat = self.calcular_papel(preco_resma, folhas_por_resma, qtd_folhas_usadas)
        custo_maq = self.calcular_producao(setup_min, tiragem_min)
        custo_total_producao = custo_mat + custo_maq + custo_acabamento

        fator_divisor = 1.0 - ((margem_lucro_desejada + self.imposto_percentual) / 100.0)

        if fator_divisor <= 0:
            raise ValueError("A soma da margem de lucro e impostos não pode ser >= 100%")

        preco_venda = custo_total_producao / fator_divisor
        lucro_valor = preco_venda * (margem_lucro_desejada / 100.0)
        imposto_valor = preco_venda * (self.imposto_percentual / 100.0)

        return {
            "Custo de Material": custo_mat,
            "Custo de Maquina": custo_maq,
            "Custo de Acabamento": custo_acabamento,
            "Custo Total de Producao": custo_total_producao,
            "Valor do Imposto": imposto_valor,
            "Lucro Estimado": lucro_valor,
            "Preco de Venda Final": preco_venda,
        }

def gerar_pdf(resultado, qtd_pecas, larg_peca, alt_peca):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Orcamento Grafico", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhes do Pedido:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 8, txt=f"Tiragem: {qtd_pecas} unidades", ln=True)
    pdf.cell(200, 8, txt=f"Formato Final: {larg_peca} x {alt_peca} cm", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resumo Financeiro:", ln=True)
    pdf.set_font("Arial", '', 12)
    
    for chave, valor in resultado.items():
        if chave == "Preco de Venda Final":
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(140, 10, txt=str(chave).upper(), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
        else:
            pdf.set_font("Arial", '', 12)
            pdf.cell(140, 10, txt=str(chave), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
            
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Orcamento gerado automaticamente. Validade de 15 dias.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE VISUAL (STREAMLIT) ---
st.set_page_config(page_title="Orçamento Gráfico", layout="wide")
st.title("🖨️ Sistema de Precificação Gráfica")

st.sidebar.header("Configurações Fixas")
custo_hora_maq = st.sidebar.number_input("Custo Hora/Máquina (R$)", value=45.00, step=5.00)
imposto_perc = st.sidebar.number_input("Imposto (%)", value=10.00, step=1.00)
sistema = PrecificadoraGrafica(custo_hora_maq, imposto_perc)

st.header("1. Aproveitamento de Corte")
col_corte1, col_corte2, col_corte3 = st.columns(3)

with col_corte1:
    st.markdown("**Folha Mãe (cm)**")
    larg_mae = st.number_input("Largura Mãe", value=66.0, step=1.0)
    alt_mae = st.number_input("Altura Mãe", value=96.0, step=1.0)

with col_corte2:
    st.markdown("**Formato Final (cm)**")
    larg_peca = st.number_input("Largura da Peça", value=21.0, step=0.5)
    alt_peca = st.number_input("Altura da Peça", value=29.7, step=0.5)

with col_corte3:
    st.markdown("**Tiragem Desejada**")
    qtd_pecas_cliente = st.number_input("Quantidade Total (ex: 1000 panfletos)", value=1000, step=100)
    perda_folhas = st.number_input("Perda/Acerto (folhas inteiras)", value=20, step=5)

rendimento = sistema.calcular_aproveitamento(larg_mae, alt_mae, larg_peca, alt_peca)

if rendimento > 0:
    folhas_necessarias_limpas = math.ceil(qtd_pecas_cliente / rendimento)
    total_folhas_usadas = folhas_necessarias_limpas + perda_folhas
else:
    total_folhas_usadas = 0
    folhas_necessarias_limpas = 0

st.info(f"**Rendimento:** Cabem {rendimento} peças por folha mãe. | **Folhas necessárias:** {folhas_necessarias_limpas} + {perda_folhas} (perda) = **{total_folhas_usadas} folhas mãe.**")

st.markdown("---")
st.header("2. Custos e Produção")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📦 Papel")
    preco_resma = st.number_input("Preço da Resma (R$)", value=150.00, step=10.00)
    folhas_resma = st.number_input("Folhas por Resma", value=500, step=50)
    st.write(f"**Folhas Calculadas:** {total_folhas_usadas}")

with col2:
    st.subheader("⚙️ Produção")
    setup_min = st.number_input("Tempo de Setup (minutos)", value=15, step=5)
    tiragem_min = st.number_input("Tempo de Tiragem (minutos)", value=30, step=5)
    custo_acab = st.number_input("Acabamento (R$)", value=20.00, step=5.00)

with col3:
    st.subheader("💰 Financeiro")
    margem_lucro = st.number_input("Margem de Lucro Desejada (%)", value=40.00, step=5.00)

st.markdown("---")
if st.button("Calcular Orçamento Completo", type="primary", use_container_width=True):
    if rendimento == 0:
        st.error("As dimensões da peça final são maiores que a folha mãe. Ajuste os tamanhos.")
    else:
        try:
            resultado = sistema.calcular_orcamento(
                preco_resma, folhas_resma, total_folhas_usadas,
                setup_min, tiragem_min, custo_acab, margem_lucro
            )
            
            st.success("Orçamento gerado com sucesso!")
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {resultado['Custo Total de Producao']:.2f}")
            r2.metric("Impostos", f"R$ {resultado['Valor do Imposto']:.2f}")
            r3.metric("Lucro Estimado", f"R$ {resultado['Lucro Estimado']:.2f}")
            r4.metric("PREÇO DE VENDA", f"R$ {resultado['Preco de Venda Final']:.2f}", delta="Final")
            
            pdf_bytes = gerar_pdf(resultado, qtd_pecas_cliente, larg_peca, alt_peca)
            
            st.markdown("---")
            st.markdown("### 📥 Enviar para o Cliente")
            
            st.download_button(
                label="📄 Baixar Orçamento em PDF",
                data=pdf_bytes,
                file_name="Orcamento_Grafico.pdf",
                mime="application/pdf"
            )
            
        except ValueError as e:
            st.error(f"Erro no cálculo: {e}")
