from fpdf import FPDF
import io

# ... (Mantenha todo o seu código de classes e entradas aqui acima) ...

# --- NOVA FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf(resultado, qtd_pecas, larg_peca, alt_peca):
    pdf = FPDF()
    pdf.add_page()
    
    # Configurações de fonte
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Orçamento Gráfico", ln=True, align='C')
    pdf.ln(10)
    
    # Informações do Pedido
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhes do Pedido:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 8, txt=f"Tiragem: {qtd_pecas} unidades", ln=True)
    pdf.cell(200, 8, txt=f"Formato Final: {larg_peca} x {alt_peca} cm", ln=True)
    pdf.ln(10)
    
    # Tabela de Custos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resumo Financeiro:", ln=True)
    pdf.set_font("Arial", '', 12)
    
    for chave, valor in resultado.items():
        # Destaca o preço final
        if chave == "Preço de Venda Final":
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(140, 10, txt=str(chave), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
        else:
            pdf.set_font("Arial", '', 12)
            pdf.cell(140, 10, txt=str(chave), border=1)
            pdf.cell(50, 10, txt=f"R$ {valor:.2f}", border=1, ln=True, align='R')
    
    # Rodapé
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Orçamento gerado automaticamente. Validade de 15 dias.", ln=True, align='C')
    
    # Retorna o PDF como bytes (compatível com Streamlit)
    return pdf.output(dest='S').encode('latin-1')

# --- BOTÃO DE CÁLCULO ---
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
            
            # Exibe na tela
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Custo Produção", f"R$ {resultado['Custo Total de Produção']:.2f}")
            r2.metric("Impostos", f"R$ {resultado['Valor do Imposto']:.2f}")
            r3.metric("Lucro Estimado", f"R$ {resultado['Lucro Estimado']:.2f}")
            r4.metric("PREÇO DE VENDA", f"R$ {resultado['Preço de Venda Final']:.2f}", delta="Final")
            
            # Gera os bytes do PDF
            pdf_bytes = gerar_pdf(resultado, qtd_pecas_cliente, larg_peca, alt_peca)
            
            st.markdown("---")
            st.markdown("### 📥 Enviar para o Cliente")
            
            # Cria o botão nativo do Streamlit para download
            st.download_button(
                label="📄 Baixar Orçamento em PDF",
                data=pdf_bytes,
                file_name="Orcamento_Grafico.pdf",
                mime="application/pdf"
            )
            
        except ValueError as e:
            st.error(f"Erro no cálculo: {e}")
