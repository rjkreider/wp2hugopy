This script converts a WordPress SQLite3 database file to markdown files.  Could probably be easily adapted to MySQL.

Title, Date, Tags, Categories, Excerpt, Featured Image and Post Content are extracted from the database file.

Frontmatter (YAML) is created for Title, Date, Tags, Categories, Excerpt, Featured Image if exists.

Original /wp-content/uploads is changed to /uploads.

Markdown files are output into a posts/ folder.

This does not handle comments, shortcodes or other custom post metadata.  Feel free to add things.
