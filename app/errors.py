# Flask는 자체 오류 페이지를 설정할 수 있는 메커니즘을 제공한다.
from flask import render_template
# from app import app, db

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     # 사용자 이름이 중복되는 등의 DB와 연결 중 500 에러 발생시, 정상적으로 이전 작업이 종료되지 않을 수 있어 rollback을 추가
#     db.session.rollback()
#     return render_template('500.html'), 500