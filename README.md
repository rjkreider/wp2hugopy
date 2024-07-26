This script converts a WordPress SQLite3 database file to markdown files.  Could probably be easily adapted to MySQL.

Following is extracted:

- Title
- Date
- Tags
- Categories
- Excerpt
- Featured Image
- Post Content

Frontmatter (YAML) is created for Title, Date, Tags, Categories, Excerpt, Featured Image if exists.

Original /wp-content/uploads is changed to /uploads.

Markdown files are output into a posts/ folder.

What is not handled:

- omments
- shortcodes
- custom post metadata
