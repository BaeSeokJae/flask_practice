from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import EditProfileForm, LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from app.forms import PostForm
from app.models import Post
import datetime

# 해당 뷰 함수는 이제 양식 데이터를 수신하기 때문에 요청 외에도 뷰 함수 POST와 관련된 두 경로의 요청을 수락함
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required # 이 라인 바로 위 링크는 인증된 사용자만 접근 가능하도록 하는 설정
def index():
# PostForm 클래스 가져오기
    form = PostForm()
    if form.validate_on_submit():
        # Post 클래스 가져오기
        post = Post(body=form.post.data, author=current_user)
        # 양식 처리 논리 Post는 데이터베이스에 새 레코드 삽입
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    # posts = current_user.followed_posts().all()
    # 템플릿 form은 텍스트 필드를 렌더링할 수 있도록 개체를 추가 인수로 받음
    return render_template("index.html", title='Home Page', form=form, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # 로그인되어있는 경우 index로 리다이렉트 시킴
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()   # 회원가입 폼 불러오기
    # 정상적인 입력값으로 확인되면 회원정보 DB에 정보 추가하기
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)

@app.route('/user/<username>')  # 동적 구성 요소 <username>
@login_required
def user(username):
    # query all로 username에 맞는 값 가져오기 시도하여 성공하면 결과 가지고, 실패하면 404 >에러 페이지 출력
    user = User.query.filter_by(username=username).first_or_404()
    # posts에 출력될 데이터 넣기
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    # 성공하면 user 변수를 user에 넣고 posts 변수를 posts에 넣어 user.html 열기
    return render_template('user.html', user=user, posts=posts)

# 마지막 방문 시간 기록
# request 되기 전에, 즉 웹페이지 view가 출력되기 전에 실행하려는 코드를 이곳에 삽입해두면 매우 유용하다.
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # 미국 시간의 9시간 뒤 = 한국 시간
        current_user.last_seen = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        db.session.commit()

# 프로필 뷰 편집 기능
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # submit으로 post 요청했을 경우
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # 웹에 접속하여 GET 요청했을 경우
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)