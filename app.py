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
        """Sugere o tamanho do espiral/wire-o baseado em papel 75g/90g"""
        if qtd_folhas <= 50: return "Espiral 9mm  |  Wire-o 3/8\" (Passo 3:1)"
        if qtd_folhas <= 100: return "Espiral 17mm |  Wire-o 5/8\" (Passo 2:1)"
        if qtd_folhas <= 120: return "Espiral 20mm |  Wire-o 3/4\" (Passo 2:1)"
        if qtd_folhas <= 200: return "Espiral 29mm |  Wire-o 1\" (Passo 2:1)"
        return "Espiral 33mm+ | Wire-o 1 1/4\" (Passo 2:1)"

    def calcular_orcamento(self, preco_resma, folhas_por_resma, total_folhas_mae, 
                           setup_min, tiragem_min, custo_acab, custo_encadernacao, margem):
        
        custo_mat = (preco_resma / folhas_por_resma) * total_folhas_mae
        custo_maq = ((setup_min + tiragem_min) / 60.0) * self.custo_hora_maquina
        custo_total_producao = custo_mat + custo_maq + custo_acab + custo_encadernacao

        fator_divisor = 1.0 - ((margem + self.imposto_percentual) / 100.0)
        if fator_divisor <= 0:
            raise ValueError("A soma da margem de lucro e impostos não pode ser >= 100%")

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
            "Preço Unitário": 0 # Será calculado na interface
        }

# --- INTERFACE VISUAL (STREAMLIT) ---
st.set_page_config(page_title="Orçamento Gráfico Premium", layout="wide")
st.title("🖨️ Sistema de Precificação Gráfica")

st.sidebar.header("Configurações Fixas")
custo_hora_maq = st.sidebar.number_input("Custo Hora/Máquina (R$)", value=45.00, step=5.00)
imposto_perc = st.sidebar.number_input("Imposto (%)", value=10.00, step=1.00)
sistema = PrecificadoraGrafica(custo_hora_maq, imposto_perc)

st.header("1. Tipo de Produto e Aproveitamento")
tipo_produto = st.radio("O que vamos orçar?", ["📄 Material Plano (Panfletos, Cartões, Cartazes)", "📔 Material Encadernado (Agendas, Cadernos, Bloquinhos)"])

colA, colB, colC = st.columns(3)
with colA:
    st.markdown("**Folha Mãe (cm)**")
    larg_mae = st.number_input("Largura Mãe", value=66.0)
    alt_mae = st.number_input("Altura Mãe", value=96.0)
with colB:
    st.markdown("**Formato Final da Peça (cm)**")
    larg_peca = st.number_input("Largura", value=15.0)
    alt_peca = st.number_input("Altura", value=21.0) # Padrão A5 para agendas
with colC:
    st.markdown("**Quantidades**")
    tiragem_cliente = st.number_input("Tiragem (Qtd de Clientes/Unidades)", value=100, step=10)
    perda_folhas = st.number_input("Perda/Acerto (folhas de máquina)", value=20, step=5)

rendimento = sistema.calcular_aproveitamento(larg_mae, alt_mae, larg_peca, alt_peca)
st.info(f"**Rendimento:** Cabem {rendimento} peças por cada folha mãe inteira.")

# --- LÓGICA DE AGENDAS VS PANFLETOS ---
custo_encadernacao_total = 0.0
total_folhas_usadas = 0

if tipo_produto == "📔 Material Encadernado (Agendas, Cadernos, Bloquinhos)":
    st.markdown("---")
    st.header("📖 Configuração do Miolo e Encadernação")
    col_ag1, col_ag2 = st.columns(2)
    
    with col_ag1:
        paginas_miolo = st.number_input("Quantas páginas tem a agenda?", value=200, step=10)
        folhas_por_unidade = math.ceil(paginas_miolo / 2)
        st.write(f"Isso significa que cada agenda usará **{folhas_por_unidade} folhas**.")
        
        # Cálculo de papel para encadernados
        if rendimento > 0:
            folhas_mae_por_agenda = folhas_por_unidade / rendimento
            total_folhas_usadas = math.ceil(folhas_mae_por_agenda * tiragem_cliente) + perda_folhas
            
    with col_ag2:
        st.success(f"💡 **Sugestão de Encadernação:** {sistema.sugerir_encadernacao(folhas_por_unidade)}")
        custo_unit_encadernacao = st.number_input("Custo do Wire-o/Espiral por unidade (R$)", value=1.50)
        custo_encadernacao_total = custo_unit_encadernacao * tiragem_cliente

else:
    # Cálculo normal para panfletos
    if rendimento > 0:
        total_folhas_usadas = math.ceil(tiragem_cliente / rendimento) + perda_folhas

st.write(f"📦 **Total de Folhas Mãe que você vai gastar:** {total_folhas_usadas} folhas.")

st.markdown("---")
st.header("2. Custos Base e Produção")
col1, col2, col3 = st.columns(3)

with col1:
    preco_resma = st.number_input("Preço da Resma (R$)", value=150.00, step=10.00)
    folhas_resma = st.number_input("Folhas por Resma", value=500, step=50)

with col2:
    setup_min = st.number_input("Tempo de Setup (minutos)", value=15, step=5)
    tiragem_min = st.number_input("Tempo de Tiragem (minutos)", value=30, step=5)
    custo_acab = st.number_input("Outros Acabamentos (Corte/Laminação) R$", value=20.00)

with col3:
    margem_lucro = st.number_input("Margem de Lucro Desejada (%)", value=40.00, step=5.00)

st.markdown("---")
if st.button("Calcular Orçamento Completo", type="primary", use_container_width=True):
    if rendimento == 0:
        st.error("As dimensões da peça final são maiores que a folha mãe!")
    else:
        try:
            res = sistema.calcular_orcamento(
                preco_resma, folhas_resma, total_folhas_usadas,
                setup_min, tiragem_min, custo_acab, custo_encadernacao_total, margem_lucro
            )
            res["Preço Unitário"] = res["Preço de Venda Final"] / tiragem_cliente
            
            st.success("Orçamento gerado com sucesso!")
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {res['Custo Total de Produção']:.2f}")
            r2.metric("Lucro Estimado", f"R$ {res['Lucro Estimado']:.2f}")
            r3.metric("PREÇO DE VENDA", f"R$ {res['Preço de Venda Final']:.2f}", delta="Total")
            r4.metric("Valor Unitário", f"R$ {res['Preço Unitário']:.2f}", delta="Por Peça")
            
            st.write("### Resumo Detalhado")
            st.json({k: f"R$ {v:.2f}" for k, v in res.items()})
            
        except ValueError as e:
            st.error(f"Erro no cálculo: {e}")
