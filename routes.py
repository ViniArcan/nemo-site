from flask import render_template, request, jsonify, redirect, url_for, flash, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import yaml
import re
import slugify
import bleach
from models import db, User, bcrypt
from flask_flatpages import FlatPages
from datetime import datetime, date

pages = FlatPages()

def register_routes(app):
    pages.init_app(app)

    @app.route('/')
    def index():
        published_pages = [p for p in pages if p.meta.get('status') == 'published']
        sorted_pages = sorted(published_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        news_posts = [p for p in sorted_pages if p.path.startswith('news/')]
        problem_post = next((p for p in sorted_pages if p.path.startswith('months-problems/') and not p.meta.get('is_solved')), None)
        return render_template('index.html', logado=current_user.is_authenticated, news_posts=news_posts, problem_post=problem_post)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email']).first()
            if user and user.check_password(request.form['password']):
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/account-settings', methods=['GET', 'POST'])
    @login_required
    def account_settings():
        if request.method == 'POST':
            if not current_user.check_password(request.form.get('current_password')):
                flash('Incorrect password. Please try again.', 'danger')
                return redirect(url_for('account_settings'))

            user = current_user
            new_email = request.form.get('email')
            if new_email != user.email and User.query.filter_by(email=new_email).first():
                flash('That email address is already in use.', 'danger')
                return redirect(url_for('account_settings'))

            user.email = new_email
            user.name = request.form.get('name')
            user.about_me = request.form.get('about_me')

            new_password = request.form.get('password')
            if new_password:
                user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

            if 'profile_pic' in request.files:
                profile_pic = request.files['profile_pic']
                if profile_pic.filename != '':
                    filename = secure_filename(profile_pic.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    profile_pic.save(image_path)
                    user.profile_image_path = image_path

            db.session.commit()
            flash('Your settings have been updated successfully!', 'success')
            return redirect(url_for('account_settings'))
        return render_template('account-settings.html', logado=current_user.is_authenticated)

    @app.route('/about')
    def about(): return render_template('about.html', logado=current_user.is_authenticated)

    @app.route('/materials')
    def materials(): return render_template('materials.html', logado=current_user.is_authenticated)

    def get_sortable_date(page):
        """Safely gets the date from post metadata, converting if necessary."""
        date_val = page.meta.get('date')
        if isinstance(date_val, date): # Handles both date and datetime objects
            # If it's datetime, convert to date; otherwise, it's already a date
            return date_val.date() if isinstance(date_val, datetime) else date_val 
        if isinstance(date_val, str):
            try:
                # Try parsing the standard YYYY-MM-DD format
                return datetime.strptime(date_val, '%Y-%m-%d').date()
            except ValueError:
                # If parsing fails, return a minimum date for consistent sorting
                pass 
        return date.min # Fallback for missing or unparseable dates

    @app.route('/months-problems')
    def months_problems():
        problem_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('months-problems/')]

        # Use the helper function in the key
        sorted_problems_by_date = sorted(problem_pages, key=get_sortable_date, reverse=True)

        current_problem = next((p for p in sorted_problems_by_date if not p.meta.get('is_solved')), None)
        solved_problems = [p for p in sorted_problems_by_date if p.meta.get('is_solved')]

        return render_template(
            'months-problems.html', 
            logado=current_user.is_authenticated, 
            current_problem=current_problem,
            solved_problems=solved_problems
        )

    @app.route('/news')
    def news():
        news_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('news/')]
        sorted_news = sorted(news_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        award_posts = [p for p in sorted_news if p.path.startswith('news/awards/')]
        other_news_posts = [p for p in sorted_news if p.path.startswith('news/others/')]
        return render_template('news.html', logado=current_user.is_authenticated, award_posts=award_posts, other_news_posts=other_news_posts)

    @app.route('/team')
    def team(): return render_template('team.html', logado=current_user.is_authenticated)

    @app.route('/faq')
    def faq(): return render_template('faq.html', logado=current_user.is_authenticated)

    @app.route('/contact')
    def contact(): return render_template('contact.html', logado=current_user.is_authenticated)

    @app.route('/post/<path:path>')
    def view_post(path):
        post = pages.get_or_404(path)
        if post.meta.get('status') == 'draft' and not current_user.is_authenticated:
            abort(404)

        author = None
        author_email = post.meta.get('author_email')
        if author_email:
            author = User.query.filter_by(email=author_email).first()

        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
            'h1', 'h2', 'h3', 'p', 'br', 'img', 'a', 'ul', 'li', 'ol',
            'strong', 'em', 'u', 's', 'blockquote', 'pre', 'code'
        ]
        allowed_attrs = {
            **bleach.sanitizer.ALLOWED_ATTRIBUTES,
            'img': ['src', 'alt', 'title'],
            'a': ['href', 'title', 'class'] 
        }
        post_html = bleach.clean(
            post.html,
            tags=allowed_tags,
            attributes=allowed_attrs
        )

        return render_template('view-post-flat.html', post=post, author=author, logado=current_user.is_authenticated, post_html=post_html)

    @app.route('/edit-post/<path:path>')
    @login_required
    def post_editor(path=None):
        post_data = {}
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    full_raw_content = f.read()

                page = pages.get(path)
                if page:
                    post_data = page.meta
                    post_data['path'] = path
                    post_data['content'] = full_raw_content
                else:
                     flash("Error parsing post metadata.", "warning")
                     return redirect(url_for('index'))

            except Exception as e:
                flash(f"Error reading file: {e}", "danger")
                return redirect(url_for('index'))
        else:
            flash("Post file not found.", "warning")
            return redirect(url_for('index'))

        return render_template('post-editor.html', post=post_data, logado=current_user.is_authenticated)

    @app.route('/save-post/<path:path>', methods=['POST'])
    @login_required
    def save_post(path):
        full_new_content = request.form.get('content')
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        if not os.path.exists(filepath):
             flash(f"Error: Cannot save, original file not found at {filepath}", "danger")
             return redirect(url_for('index'))

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_new_content)
            flash("Post content updated successfully!", "success")
            pages.reload()
            return redirect(url_for('view_post', path=path))
        except Exception as e:
            flash(f"Error saving file: {e}", "danger")
            return redirect(url_for('post_editor', path=path))

    @app.route('/create-post')
    @login_required
    def create_post_view():
        return render_template('create-post.html', logado=current_user.is_authenticated)

    @app.route('/create-post-save', methods=['POST'])
    @login_required
    def create_post_save():
        full_content = request.form.get('full_content')
        if not full_content:
            flash("Content cannot be empty.", "danger")
            return redirect(url_for('create_post_view'))

        try:
            match = re.match(r'^---\s*(.*?)\s*---\s*(.*)', full_content, re.DOTALL)
            if not match: raise ValueError("Could not find YAML front-matter separator '---'")

            yaml_string = match.group(1)
            metadata = yaml.safe_load(yaml_string)
            if not metadata or not isinstance(metadata, dict):
                raise ValueError("Invalid YAML front-matter format")

            title = metadata.get('title')
            if not title: raise ValueError("Metadata must contain a 'title'")

        except (yaml.YAMLError, ValueError) as e:
            flash(f"Error parsing Markdown file: {e}", "danger")
            return redirect(url_for('create_post_view'))

        user_filename = request.form.get('filename_base', '').strip()
        filename_base = slugify.slugify(user_filename) if user_filename else slugify.slugify(title)

        post_type = metadata.get('post_type', 'misc')
        if post_type == 'News':
            category = metadata.get('category', 'General').strip().lower()
            directory = 'news/awards' if category == 'award' else 'news/others'
        elif post_type == 'Month-Problem':
            directory = 'months-problems'
        else:
            directory = 'misc'

        counter = 0
        filename = f"{filename_base}.md"
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], directory, filename)
        while os.path.exists(filepath):
            counter += 1
            filename = f"{filename_base}-{counter}.md"
            filepath = os.path.join(app.config['FLATPAGES_ROOT'], directory, filename)

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

            flash("New post created successfully!", "success")
            pages.reload()

            page_path = os.path.join(directory, filename_base + (f"-{counter}" if counter > 0 else ""))
            return redirect(url_for('view_post', path=page_path))

        except IOError as e:
            flash(f"Error saving file: {e}", "danger")
            return redirect(url_for('create_post_view'))

    @app.route('/delete-post/<path:path>', methods=['POST'])
    @login_required
    def delete_post_file(path):
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                flash(f"Post '{path}' deleted successfully.", "success")
                pages.reload()
                return redirect(url_for('drafts'))
            except OSError as e:
                flash(f"Error deleting file: {e}", "danger")
                return redirect(url_for('drafts'))
        else:
            flash("Error: Post file not found.", "warning")
            return redirect(url_for('drafts'))

    @app.route('/drafts')
    @login_required
    def drafts():
        draft_pages = [p for p in pages if p.meta.get('status') == 'draft']
        sorted_drafts = sorted(draft_pages, key=lambda p: p.meta.get('date', datetime.min), reverse=True)
        return render_template('drafts.html', post_list=sorted_drafts, logado=current_user.is_authenticated)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'webm', 'mp4', 'mp3', 'wav', 'ogg', 'svg', 'pdf'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/upload-asset', methods=['POST'])
    @login_required
    def upload_asset():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(save_path)
                file_url = url_for('static', filename=os.path.join('uploads', filename))

                file_extension = filename.rsplit('.', 1)[1].lower()
                if file_extension in {'png', 'jpg', 'jpeg', 'gif'}:
                    markdown_link = f"![{filename}]({file_url})"
                else:
                    markdown_link = f"[{filename}]({file_url})"

                return jsonify({'markdownLink': markdown_link}), 200

            except Exception as e:
                return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'File type not allowed'}), 400
