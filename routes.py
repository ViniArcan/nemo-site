from flask import render_template, request, jsonify, redirect, url_for, flash, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date # Import date as well
import yaml
import re
import slugify
import bleach # Used for sanitizing HTML output
from models import db, User, bcrypt
from flask_flatpages import FlatPages

# Initialize Flask-FlatPages extension
pages = FlatPages()

# Function to register all routes with the Flask app instance
def register_routes(app):
    # Initialize FlatPages with the app context
    pages.init_app(app)

    # --- Public Routes ---

    ## Home Page
    @app.route('/')
    def index():
        # Get all pages marked as 'published'
        published_pages = [p for p in pages if p.meta.get('status') == 'published']
        # Sort pages by date, newest first, using current time as fallback
        sorted_pages = sorted(published_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        # Get the 6 most recent news posts
        news_posts = [p for p in sorted_pages if p.path.startswith('news/')][:6]
        # Get the current "Problem of the Month" (first one found that isn't solved)
        problem_post = next((p for p in sorted_pages if p.path.startswith('months-problems/') and not p.meta.get('is_solved')), None)
        # Render the index template with the fetched posts
        return render_template('index.html', 
                               logado=current_user.is_authenticated, 
                               news_posts=news_posts, 
                               problem_post=problem_post,
                               title="NEMO Home") # Add title

    ## Login Page
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Find user by email
            user = User.query.filter_by(email=request.form['email']).first()
            # Check if user exists and password is correct
            if user and user.check_password(request.form['password']):
                # Log the user in with Flask-Login
                login_user(user, remember=True) # Remember session across browser closes
                return redirect(url_for('index'))
            else:
                # Show error message if login fails
                flash('Invalid credentials.', 'danger')
        # Render login page (handles GET requests and failed POST requests)
        return render_template('login.html', title="Login")

    ## Logout Action
    @app.route('/logout')
    @login_required # Protect this route: only logged-in users can logout
    def logout():
        # Log the user out
        logout_user()
        return redirect(url_for('index'))

    ## About Page
    @app.route('/about')
    def about(): 
        return render_template('about.html', 
                               logado=current_user.is_authenticated,
                               title="Sobre") # Add title

    ## Materials Page
    @app.route('/materials')
    def materials(): 
        return render_template('materials.html', 
                               logado=current_user.is_authenticated,
                               title="Materiais") # Add title

    # --- Helper Function for Sorting by Date ---
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

    ## Problems of the Month Page
    @app.route('/months-problems')
    def months_problems():
        # Get all published problem pages
        problem_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('months-problems/')]

        # Sort problems using the safer helper function
        sorted_problems_by_date = sorted(problem_pages, key=get_sortable_date, reverse=True)

        # Find the first problem in the sorted list that isn't marked as solved
        current_problem = next((p for p in sorted_problems_by_date if not p.meta.get('is_solved')), None)
        # Get all problems marked as solved
        solved_problems = [p for p in sorted_problems_by_date if p.meta.get('is_solved')]

        return render_template(
            'months-problems.html', 
            logado=current_user.is_authenticated, 
            current_problem=current_problem,
            solved_problems=solved_problems,
            title="Problemas do Mês" # Add title
        )

    ## News Overview Page (Shows sliders)
    @app.route('/news')
    def news():
        # Get all published news pages
        news_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('news/')]
        # Sort news by date (using simpler lambda, assumes date is valid datetime or missing)
        sorted_news = sorted(news_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        # Filter for award posts
        award_posts = [p for p in sorted_news if p.path.startswith('news/awards/')]
        # Filter for other general news posts
        other_news_posts = [p for p in sorted_news if p.path.startswith('news/others/')]
        return render_template('news.html', 
                               logado=current_user.is_authenticated, 
                               award_posts=award_posts, 
                               other_news_posts=other_news_posts,
                               title="Notícias") # Add title
    
    ## News Awards Page (List View)
    @app.route('/news-awards')
    def news_awards():
        news_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('news/')]
        sorted_news = sorted(news_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        award_posts = [p for p in sorted_news if p.path.startswith('news/awards/')]
        return render_template(
            'news-awards.html', 
            logado=current_user.is_authenticated, 
            award_posts=award_posts,
            title="Prêmios e Conquistas" # Pass a title for the <title> tag
        )
    
    ## News General Page (List View)
    @app.route('/news-general')
    def news_general():
        news_pages = [p for p in pages if p.meta.get('status') == 'published' and p.path.startswith('news/')]
        sorted_news = sorted(news_pages, key=lambda p: p.meta.get('date', datetime.now()), reverse=True)
        other_news_posts = [p for p in sorted_news if p.path.startswith('news/others/')]
        return render_template(
            'news-general.html', 
            logado=current_user.is_authenticated, 
            other_news_posts=other_news_posts,
            title="Notícias Gerais" # Pass a title for the <title> tag
        )

    ## Team Page (Note: Seems unused currently, template may not exist)
    # @app.route('/team')
    # def team(): return render_template('team.html', logado=current_user.is_authenticated, title="Equipe")

    ## FAQ Page
    @app.route('/faq')
    def faq(): 
        return render_template('faq.html', 
                               logado=current_user.is_authenticated,
                               title="FAQ") # Add title

    ## Contact Page
    @app.route('/contact')
    def contact(): 
        return render_template('contact.html', 
                               logado=current_user.is_authenticated,
                               title="Contato") # Add title

    ## View Single Post Page
    # The <path:path> converter allows slashes in the URL path
    @app.route('/post/<path:path>')
    def view_post(path):
        # Get the FlatPage object or return a 404 error if not found
        post = pages.get_or_404(path)
        # If the post is a draft, only show it to logged-in users
        if post.meta.get('status') == 'draft' and not current_user.is_authenticated:
            abort(404) # Return 404 for non-logged-in users trying to view drafts

        # Find the author's User object based on email in metadata, if provided
        author = None
        author_email = post.meta.get('author_email')
        if author_email:
            author = User.query.filter_by(email=author_email).first()

        # --- HTML Sanitization using Bleach ---
        # Define allowed HTML tags (start with defaults and add necessary ones)
        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
            'h1', 'h2', 'h3', 'p', 'br', 'img', 'a', 'ul', 'li', 'ol',
            'strong', 'em', 'u', 's', 'blockquote', 'pre', 'code'
        ]
        # Define allowed attributes for specific tags
        allowed_attrs = {
            **bleach.sanitizer.ALLOWED_ATTRIBUTES, # Include default allowed attributes
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'a': ['href', 'title', 'class'] 
        }
        # Sanitize the HTML rendered from Markdown to prevent XSS attacks
        post_html = bleach.clean(
            post.html, # The HTML generated by Flask-FlatPages' Markdown processor
            tags=allowed_tags,
            attributes=allowed_attrs
        )
        # --- End Sanitization ---

        # Render the template to display the post
        return render_template('view-post-flat.html', 
                               post=post, 
                               author=author, 
                               logado=current_user.is_authenticated, 
                               post_html=post_html,
                               title=post.meta.get('title', 'Post')) # Use post title for page title

    # --- Admin Routes ---

    ## Account Settings Page
    @app.route('/account-settings', methods=['GET', 'POST'])
    @login_required # Protect this route
    def account_settings():
        if request.method == 'POST':
            # Verify current password before allowing changes
            if not current_user.check_password(request.form.get('current_password')):
                flash('Incorrect password. Please try again.', 'danger')
                return redirect(url_for('account_settings'))

            user = current_user # Get the currently logged-in user object
            
            # Check if the new email is different and already exists
            new_email = request.form.get('email')
            if new_email != user.email and User.query.filter_by(email=new_email).first():
                flash('That email address is already in use.', 'danger')
                return redirect(url_for('account_settings'))

            # Update user fields
            user.email = new_email
            user.name = request.form.get('name')
            user.about_me = request.form.get('about_me')

            # Update password only if a new one is provided
            new_password = request.form.get('password')
            if new_password:
                user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Handle profile picture upload
            if 'profile_pic' in request.files:
                profile_pic = request.files['profile_pic']
                if profile_pic.filename != '': # Check if a file was actually selected
                    filename = secure_filename(profile_pic.filename) # Sanitize filename
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    profile_pic.save(image_path)
                    user.profile_image_path = image_path # Update user's profile image path

            # Commit changes to the database
            db.session.commit()
            flash('Your settings have been updated successfully!', 'success')
            return redirect(url_for('account_settings'))
        
        # Render the settings page for GET requests
        return render_template('account-settings.html', 
                               logado=current_user.is_authenticated,
                               title="Account Settings") # Add title

    ## Edit Post Page (Loads content into editor)
    @app.route('/edit-post/<path:path>')
    @login_required # Protect this route
    def post_editor(path): # Changed default path=None as it's required by the route
        post_data = {} # Dictionary to hold post data for the template
        # Construct the full path to the markdown file
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        if os.path.exists(filepath):
            try:
                # Read the entire raw content of the file (including front-matter)
                with open(filepath, 'r', encoding='utf-8') as f:
                    full_raw_content = f.read()

                # Use FlatPages to parse the metadata separately
                page = pages.get(path) 
                if page:
                    post_data = page.meta # Get metadata (title, date, etc.)
                    post_data['path'] = path # Add path for context
                    post_data['title'] = page.meta.get('title', 'Untitled') # Ensure title exists
                    post_data['content'] = full_raw_content # Add the raw content for the editor
                else:
                     # This might happen if the file exists but FlatPages fails to parse it
                     flash("Error parsing post metadata.", "warning")
                     return redirect(url_for('index')) # Redirect to index on parsing error

            except Exception as e:
                flash(f"Error reading file: {e}", "danger")
                return redirect(url_for('index')) # Redirect on file read error
        else:
            flash("Post file not found.", "warning")
            return redirect(url_for('index')) # Redirect if file doesn't exist

        # Render the editor template with the loaded post data
        return render_template('post-editor.html', 
                               post=post_data, 
                               logado=current_user.is_authenticated,
                               title=f"Edit: {post_data.get('title', 'Post')}") # Use post title

    ## Save Post Action (Handles POST from editor)
    @app.route('/save-post/<path:path>', methods=['POST'])
    @login_required # Protect this route
    def save_post(path):
        # Get the full new content submitted from the editor textarea
        full_new_content = request.form.get('content')
        # Construct the full path to the markdown file
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        # Security check: Ensure the file we are about to overwrite actually exists
        if not os.path.exists(filepath):
             flash(f"Error: Cannot save, original file not found at {filepath}", "danger")
             return redirect(url_for('index'))

        try:
            # Write the new content, overwriting the old file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_new_content)
            flash("Post content updated successfully!", "success")
            # Reload FlatPages cache to reflect changes immediately
            pages.reload() 
            # Redirect the user back to view the updated post
            return redirect(url_for('view_post', path=path))
        except Exception as e:
            flash(f"Error saving file: {e}", "danger")
            # Redirect back to the editor if saving failed
            return redirect(url_for('post_editor', path=path))

    ## Create New Post Page (Shows blank editor with template)
    @app.route('/create-post')
    @login_required # Protect this route
    def create_post_view():
        # Render the create post template
        return render_template('create-post.html', 
                               logado=current_user.is_authenticated,
                               title="Create New Post") # Add title

    ## Create New Post Action (Handles POST from create form)
    @app.route('/create-post-save', methods=['POST'])
    @login_required # Protect this route
    def create_post_save():
        # Get the full content (including front-matter) from the form
        full_content = request.form.get('full_content')
        if not full_content:
            flash("Content cannot be empty.", "danger")
            return redirect(url_for('create_post_view'))

        # --- Parse Metadata and Content ---
        try:
            # Use regex to separate YAML front-matter from Markdown content
            # Looks for '---' at the start, captures YAML block, then captures the rest
            match = re.match(r'^---\s*(.*?)\s*---\s*(.*)', full_content, re.DOTALL)
            if not match: raise ValueError("Could not find YAML front-matter separator '---'")

            yaml_string = match.group(1) # The captured YAML block
            # Parse the YAML string into a Python dictionary
            metadata = yaml.safe_load(yaml_string)
            if not metadata or not isinstance(metadata, dict):
                raise ValueError("Invalid YAML front-matter format")

            # Extract the title, which is required for filename generation
            title = metadata.get('title')
            if not title: raise ValueError("Metadata must contain a 'title'")

        except (yaml.YAMLError, ValueError) as e:
            # Handle errors during parsing (invalid YAML, missing title, etc.)
            flash(f"Error parsing Markdown file: {e}", "danger")
            return redirect(url_for('create_post_view'))
        # --- End Parsing ---

        # --- Determine Filename and Directory ---
        # Get optional filename base from form, otherwise generate from title
        user_filename = request.form.get('filename_base', '').strip()
        # Slugify the name (convert to lowercase, replace spaces with hyphens, remove special chars)
        filename_base = slugify.slugify(user_filename) if user_filename else slugify.slugify(title)

        # Determine the subdirectory based on post_type and category metadata
        post_type = metadata.get('post_type', 'misc') # Default to 'misc'
        if post_type == 'News':
            category = metadata.get('category', 'General').strip().lower()
            directory = 'news/awards' if category == 'award' else 'news/others'
        elif post_type == 'Month-Problem':
            directory = 'months-problems'
        else: # Fallback for unknown types or 'misc'
            directory = 'misc' 

        # --- Check for Existing Files and Generate Unique Name ---
        counter = 0
        filename = f"{filename_base}.md"
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], directory, filename)
        # If a file with the same name exists, append '-1', '-2', etc. until a unique name is found
        while os.path.exists(filepath):
            counter += 1
            filename = f"{filename_base}-{counter}.md"
            filepath = os.path.join(app.config['FLATPAGES_ROOT'], directory, filename)
        # --- End File Naming ---
        
        # --- Save the File ---
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Write the full content to the new file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

            flash("New post created successfully!", "success")
            # Reload FlatPages cache to include the new post
            pages.reload()

            # Construct the path used by Flask-FlatPages (directory + base filename without extension)
            page_path = os.path.join(directory, filename_base + (f"-{counter}" if counter > 0 else ""))
            # Redirect to view the newly created post
            return redirect(url_for('view_post', path=page_path))

        except IOError as e:
            flash(f"Error saving file: {e}", "danger")
            return redirect(url_for('create_post_view'))
        # --- End Save ---

    ## Delete Post Action (Handles POST from button/form)
    @app.route('/delete-post/<path:path>', methods=['POST'])
    @login_required # Protect this route
    def delete_post_file(path):
        # Construct the full path to the markdown file
        filepath = os.path.join(app.config['FLATPAGES_ROOT'], path + '.md')

        if os.path.exists(filepath):
            try:
                # Delete the file from the filesystem
                os.remove(filepath)
                flash(f"Post '{path}' deleted successfully.", "success")
                # Reload FlatPages cache to remove the deleted post
                pages.reload()
                # Redirect back to the drafts page (or another appropriate page)
                return redirect(url_for('drafts'))
            except OSError as e:
                flash(f"Error deleting file: {e}", "danger")
                return redirect(url_for('drafts')) # Redirect even if deletion fails
        else:
            flash("Error: Post file not found.", "warning")
            return redirect(url_for('drafts')) # Redirect if file doesn't exist

    ## Drafts Page (Lists posts marked as draft)
    @app.route('/drafts')
    @login_required # Protect this route
    def drafts():
        # Get all pages with status 'draft'
        draft_pages = [p for p in pages if p.meta.get('status') == 'draft']
        # Sort drafts by date, newest first (using min date as fallback)
        sorted_drafts = sorted(draft_pages, key=lambda p: p.meta.get('date', datetime.min), reverse=True)
        # Render the drafts template
        return render_template('drafts.html', 
                               post_list=sorted_drafts, 
                               logado=current_user.is_authenticated,
                               title="Drafts") # Add title

    # --- Asset Upload Helper ---
    # Define allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'webm', 'mp4', 'mp3', 'wav', 'ogg', 'svg', 'pdf'}

    # Helper function to check if a filename has an allowed extension
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    ## Upload Asset Endpoint (Handles file uploads from editor)
    @app.route('/upload-asset', methods=['POST'])
    @login_required # Protect this route
    def upload_asset():
        # Basic checks for file presence
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Check if file type is allowed and save it
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # Sanitize filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(save_path) # Save the file
                # Generate the URL for the saved file
                # Uses url_for('static', ...) which points to the /static folder
                file_url = url_for('static', filename=os.path.join('uploads', filename))

                # --- Generate Markdown Link ---
                # Check file extension to decide if it's an image or other link
                file_extension = filename.rsplit('.', 1)[1].lower()
                if file_extension in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}: # Added svg/webp
                    markdown_link = f"![{filename}]({file_url})" # Image syntax
                else:
                    markdown_link = f"[{filename}]({file_url})" # Regular link syntax
                # --- End Link Generation ---

                # Return the Markdown link as JSON
                return jsonify({'markdownLink': markdown_link}), 200

            except Exception as e:
                # Return error if saving fails
                return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        else:
            # Return error if file type is not allowed
            return jsonify({'error': 'File type not allowed'}), 400
