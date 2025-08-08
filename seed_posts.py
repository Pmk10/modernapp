# seed_posts.py
from app import create_app, db
from models import User, Category, Tag, BlogPost

app = create_app()
app.app_context().push()

# 1. Ensure admin user exists
admin = User.query.filter_by(email='admin@example.com').first()

# 2. Ensure categories exist (names must match your categories table)
category_map = {}
for name in ["Tutorial", "Framework", "JavaScript", "CSS", "Accessibility"]:
    cat = Category.query.filter_by(name=name).first()
    if not cat:
        cat = Category(name=name, description=f"{name} articles")
        db.session.add(cat)
    category_map[name] = cat

# 3. Ensure tags exist
tag_map = {}
tags = ["HTML", "CSS", "JavaScript", "Bootstrap", "ES6", "Responsive", 
        "Features", "Grid", "Flexbox", "A11y", "ARIA","Accessibility"]
for t in tags:
    tag = Tag.query.filter_by(name=t).first()
    if not tag:
        tag = Tag(name=t)
        db.session.add(tag)
    tag_map[t] = tag

db.session.commit()

# 4. Define your posts data
posts_data = [
    {
        "title": "Getting Started with Modern Frontend Development",
        "excerpt": "Learn the essentials of HTML5, CSS3, and ES6 JavaScript for building modern web applications.",
        "content": "<p>Learn the essentials of HTML5, CSS3, and ES6 JavaScript for building modern web applications.</p>",
        "author": admin,
        "category": category_map["Tutorial"],
        "tags": ["HTML", "CSS", "JavaScript"],
        "read_time": "5 min read",
        "featured": True
    },
    {
        "title": "Bootstrap 5: Building Responsive Layouts",
        "excerpt": "Master the Bootstrap 5 grid system and component library for rapid web development.",
        "content": "<p>Master the Bootstrap 5 grid system and component library for rapid web development.</p>",
        "author": admin,
        "category": category_map["Framework"],
        "tags": ["Bootstrap", "CSS", "Responsive"],
        "read_time": "8 min read"
    },
    {
        "title": "JavaScript ES6 Features Every Developer Should Know",
        "excerpt": "Explore arrow functions, template literals, destructuring, and other powerful ES6 features.",
        "content": "<p>Explore arrow functions, template literals, destructuring, and other powerful ES6 features.</p>",
        "author": admin,
        "category": category_map["JavaScript"],
        "tags": ["ES6", "JavaScript", "Features"],
        "read_time": "12 min read"
    },
    {
        "title": "CSS Grid vs Flexbox: When to Use Which",
        "excerpt": "Understanding the differences between CSS Grid and Flexbox and their ideal use cases.",
        "content": "<p>Understanding the differences between CSS Grid and Flexbox and their ideal use cases.</p>",
        "author": admin,
        "category": category_map["CSS"],
        "tags": ["CSS", "Grid", "Flexbox"],
        "read_time": "6 min read"
    },
    {
        "title": "Building Accessible Web Applications",
        "excerpt": "Learn how to create inclusive web experiences that work for all users.",
        "content": "<p>Learn how to create inclusive web experiences that work for all users.</p>",
        "author": admin,
        "category": category_map["Accessibility"],
        "tags": ["A11y", "ARIA", "Accessibility"],
        "read_time": "10 min read"
    }
]

# 5. Insert posts
for pdata in posts_data:
    post = BlogPost(
        title=pdata["title"],
        excerpt=pdata["excerpt"],
        content=pdata["content"],
        author_id=pdata["author"].id,
        category_id=pdata["category"].id,
        read_time=pdata.get("read_time", "5 min read"),
        featured=pdata.get("featured", False)
    )
    for tag_name in pdata["tags"]:
        post.tags.append(tag_map[tag_name])
    db.session.add(post)

db.session.commit()
print("✅ Seeded 5 blog posts successfully!")
