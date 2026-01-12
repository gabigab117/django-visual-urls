import os
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

class Command(BaseCommand):
    help = "Génère un fichier HTML avec la cartographie des URLs du projet."

    def handle(self, *args, **options):
        self.stdout.write("🔍 Analyse des URLs en cours...")
        
        # 1. Récupérer toutes les URLs
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        nodes, edges = self.extract_graph_data(url_patterns)

        # 2. Générer le code Mermaid
        mermaid_code = "graph LR\n"
        # Définition des styles (optionnel mais plus joli)
        mermaid_code += "    classDef view fill:#f9f,stroke:#333,stroke-width:2px;\n"
        mermaid_code += "    classDef url fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;\n"

        for node in nodes:
            # On nettoie les ID pour éviter les bugs Mermaid
            clean_id = self.clean_str(node['id'])
            label = node['label']
            css_class = node['type']
            mermaid_code += f'    {clean_id}["{label}"]:::{css_class}\n'

        for edge in edges:
            src = self.clean_str(edge['source'])
            dst = self.clean_str(edge['target'])
            mermaid_code += f'    {src} --> {dst}\n'

        # 3. Créer le HTML final
        html_content = self.get_html_template(mermaid_code)

        # 4. Écriture du fichier
        output_file = "url_map.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.stdout.write(self.style.SUCCESS(f"✅ Terminé ! Fichier généré : {os.path.abspath(output_file)}"))

    def extract_graph_data(self, urlpatterns, prefix="/"):
        """Fonction récursive pour extraire les noeuds et les liens"""
        nodes = []
        edges = []

        # Création du noeud racine pour ce niveau
        root_id = f"url_{prefix}"
        nodes.append({'id': root_id, 'label': prefix, 'type': 'url'})

        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                # C'est un 'include', on descend plus profond
                new_prefix = prefix + str(pattern.pattern)
                sub_nodes, sub_edges = self.extract_graph_data(pattern.url_patterns, new_prefix)
                
                nodes.extend(sub_nodes)
                edges.extend(sub_edges)
                
                # On lie le dossier parent au dossier enfant
                child_root_id = f"url_{new_prefix}"
                edges.append({'source': root_id, 'target': child_root_id})

            elif isinstance(pattern, URLPattern):
                # C'est une vue finale
                full_url = prefix + str(pattern.pattern)
                # Nettoyage des caractères regex de Django (^, $)
                full_url = full_url.replace('^', '').replace('$', '')
                
                # Nom de la vue
                if hasattr(pattern.callback, '__name__'):
                    view_name = pattern.callback.__name__
                    module_name = pattern.callback.__module__
                    full_view_name = f"{module_name}.{view_name}"
                else:
                    full_view_name = str(pattern.callback)

                view_id = f"view_{full_view_name}"
                
                # Ajout du noeud Vue
                nodes.append({'id': view_id, 'label': view_name, 'type': 'view'})
                # Lien URL -> Vue
                edges.append({'source': root_id, 'target': view_id})

        return nodes, edges

    def clean_str(self, text):
        """Nettoie les chaînes pour qu'elles soient des IDs Mermaid valides"""
        return text.replace("/", "_").replace(".", "_").replace("-", "_").replace(":", "_").replace("<", "").replace(">", "")

    def get_html_template(self, mermaid_content):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Django Visual URLs</title>
            <style>
                body {{ font-family: sans-serif; background: #f4f4f4; padding: 20px; }}
                h1 {{ text-align: center; color: #333; }}
                .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <h1>Cartographie des URLs Django</h1>
            <div class="container">
                <pre class="mermaid">
{mermaid_content}
                </pre>
            </div>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true }});
            </script>
        </body>
        </html>
        """