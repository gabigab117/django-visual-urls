from pathlib import Path
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

class Command(BaseCommand):
    help = "Generate a visual map of Django URLs using Mermaid.js"

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-admin',
            action='store_true',
            help="Include Django admin URLs in the visualization",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Analyzing URLs...")
        
        include_admin = options['include_admin']

        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        nodes, edges = self.extract_graph_data(url_patterns, include_admin=include_admin)
        # https://mermaid.ai/open-source/ecosystem/tutorials.html
        mermaid_code = "graph LR\n"
        
        # Define CSS classes for different node types
        mermaid_code += "    classDef url fill:#4A90E2,stroke:#2E5C8A,color:#fff\n"
        mermaid_code += "    classDef view fill:#7ED321,stroke:#5FA319,color:#fff\n"

        for node in nodes:
            clean_id = self.clean_str(node['id'])
            label = node['label']
            node_type = node['type']
            mermaid_code += f'    {clean_id}["{label}"]:::{node_type}\n'

        for edge in edges:
            src = self.clean_str(edge['source'])
            dst = self.clean_str(edge['target'])
            mermaid_code += f'    {src} --> {dst}\n'

        html_content = self.get_html_template(mermaid_code)

        output_file = "url_map.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.stdout.write(self.style.SUCCESS(f"✅ Done! File generated: {Path(output_file).resolve()}"))
        
    def extract_graph_data(self, urlpatterns, prefix="/", include_admin=False):
        """
        Recursively extract nodes and edges from urlpatterns.
        """
        nodes = []
        edges = []

        # Create the root node for this level
        root_id = f"url_{prefix}"
        nodes.append({'id': root_id, 'label': prefix, 'type': 'url'})

        for pattern in urlpatterns:
            # Check for admin exclusion
            pattern_str = str(pattern.pattern)
            is_admin_url = pattern_str.lstrip('^').startswith('admin/')
            if not include_admin and is_admin_url:
                continue

            if isinstance(pattern, URLResolver):
                # It's an 'include', we go deeper
                new_prefix = prefix + str(pattern.pattern)
                sub_nodes, sub_edges = self.extract_graph_data(pattern.url_patterns, new_prefix, include_admin=include_admin)
                
                nodes.extend(sub_nodes)
                edges.extend(sub_edges)
                
                # Link parent folder to child folder
                child_root_id = f"url_{new_prefix}"
                edges.append({'source': root_id, 'target': child_root_id})

            elif isinstance(pattern, URLPattern):
                # It's a final view
                full_url = prefix + str(pattern.pattern)
                # Clean Django regex characters (^, $)
                full_url = full_url.replace('^', '').replace('$', '')
                
                # View name
                if hasattr(pattern.callback, '__name__'):
                    view_name = pattern.callback.__name__
                    module_name = pattern.callback.__module__
                    full_view_name = f"{module_name}.{view_name}"
                else:
                    full_view_name = str(pattern.callback)

                view_id = f"view_{full_view_name}"
                
                # Add the view node
                nodes.append({'id': view_id, 'label': view_name, 'type': 'view'})
                # Link URL -> View
                edges.append({'source': root_id, 'target': view_id})

        return nodes, edges

    def clean_str(self, text: str) -> str:
        """
        Example: "/api/v1/users/<int:id>/" -> "_api_v1_users_int_id_"
        """
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
            <h1>Django URL Map</h1>
            <div class="container">
                <pre class="mermaid">
                    {mermaid_content}
                </pre>
            </div>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true }});
            </script>
        </body>
        </html>
        """