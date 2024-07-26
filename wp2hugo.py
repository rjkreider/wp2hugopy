import sqlite3
import os
import re
import unicodedata
import datetime
import yaml
from html2text import HTML2Text  # Import the class directly

# Function to convert image URLs
def convert_image_url(url):
    return re.sub(r'wp-content', 'uploads', url)

# Function to extract tags and categories from the database
def get_terms(conn, post_id, taxonomy):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name
        FROM wp_terms t
        INNER JOIN wp_term_taxonomy tt ON tt.term_id = t.term_id
        INNER JOIN wp_term_relationships tr ON tr.term_taxonomy_id = tt.term_taxonomy_id
        WHERE tr.object_id = ? AND tt.taxonomy = ?
    """, (post_id, taxonomy))
    return [row[0] for row in cursor.fetchall()]

# Function to create a slug from the post title
def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-zA-Z0-9\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

# Function to escape YAML special characters
def escape_yaml(value):
    return yaml.safe_dump(value, default_flow_style=False).strip()

# Function to convert HTML to Markdown, preserving <pre> and <code> blocks
def html_to_markdown(html):
    # Use HTML2Text to convert HTML to Markdown
    html_to_md = HTML2Text()
    html_to_md.body_width = 0
    markdown = html_to_md.handle(html)
    
    # Preserve <pre> and <code> blocks
    markdown = re.sub(r'<pre>(.*?)</pre>', lambda m: f'```{m.group(1)}```', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<code>(.*?)</code>', lambda m: f'`{m.group(1)}`', markdown, flags=re.DOTALL)
    
    return markdown

# Function to export posts to markdown
def export_posts_to_markdown(db_path, output_dir):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID, post_title, post_excerpt, post_content, post_date, post_type
        FROM wp_posts
        WHERE post_type = 'post' AND post_status = 'publish'
    """)

    posts = cursor.fetchall()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for post in posts:
        post_id, title, excerpt, content, post_date, post_type = post
        tags = get_terms(conn, post_id, 'post_tag')
        categories = get_terms(conn, post_id, 'category')

        # Convert image URLs in the content
        content = re.sub(r'src="([^"]*wp-content[^"]*)"', lambda match: f'src="{convert_image_url(match.group(1))}"', content)

        # Convert HTML content to Markdown
        content = html_to_markdown(content)

        # Prepare front matter
        front_matter = {
            'title': escape_yaml(title),
            'date': datetime.datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S').isoformat(),
            'tags': tags,
            'categories': categories,
        }

        if excerpt:
            front_matter['excerpt'] = escape_yaml(excerpt)
        # Logic for featured_image should be added here if available

        # Convert front matter to YAML format
        front_matter_yaml = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True).strip()

        # Create the markdown content with front matter
        markdown_content = f"---\n{front_matter_yaml}\n---\n\n{content}\n"

        # Create slug for the filename
        filename = f"{slugify(title)}.md"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    conn.close()

# Example usage
db_path = 'db.sqlite'
output_dir = 'posts'
export_posts_to_markdown(db_path, output_dir)
