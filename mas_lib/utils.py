from langchain_core.runnables.graph_mermaid import draw_mermaid_png

def create_mermaid_graph(app):
    mermaid_syntax = app.get_graph().draw_mermaid()

    png_bytes = draw_mermaid_png(
        mermaid_syntax,
        output_file_path="workflow_graph.png",
        background_color="white",
        padding=10
    )