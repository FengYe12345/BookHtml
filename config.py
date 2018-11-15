from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost/first_flask"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.secret_key = 'iii'

db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    #     引用 books给自己用 ，author是给Book模型用
    books = relationship('Book', backref='author')

    def __repr__(self):
        return 'Author: %s' % self.name


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Book: %s %s' % (self.name, self.author_id)


# 自定义表单类
class AuthorForm(FlaskForm):
    author = StringField(u'作者', validators=[DataRequired()])
    book = StringField(u'书籍', validators=[DataRequired()])
    submit = SubmitField(u'提交')


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 1.查询数据库
    author = Author.query.get(author_id)
    if author:
        try:
            Book.query.filter_by(author_id=author_id).delete()
    #       删除作者
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者出错')
            db.session.rollback()
    else:
        flash('作者找不到')
    return redirect(url_for('index'))
@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # 查询数据库，是否有该ID的书，如果有就删除，没有就提示错误
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
            db.session.rollback()
    else:
        flash('书籍找不到')
    # 如何返回当前网址 -->重定向
    # redirect：重定向，需要传入网络/路由地址
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    # 查询所有的作者信息，让信息传递给模板
    # 创建自定义表单类
    """
       验证逻辑：
       1.调用TF的函数实现验证
       2.验证通过获取数据
       3.判断作者是否存在
       4.如果作者存在，判断书籍是否存在，没有重复书籍就添加数据，如果重复就提示错误
       5.如果作者不存在，添加作者和书籍
       6.验证不通过就提示错误
   """
    author_form = AuthorForm()
    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data
        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已存在同样书籍')
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()
                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加书籍和作者失败')
                db.session.rollback()
    else:
        if request.method == 'POST':
            flash('参数不全')

    author_form = AuthorForm()
    authors = Author.query.all()
    return render_template('books.html', authors=authors, form=author_form)


db.drop_all()
db.create_all()
au1 = Author(name='小王')
au2 = Author(name='jack')
au3 = Author(name='mike')
db.session.add_all([au1, au2, au3])
db.session.commit()
bk1 = Book(name='python', author_id=au1.id)
bk2 = Book(name='java', author_id=au1.id)
bk3 = Book(name='c++', author_id=au2.id)
bk4 = Book(name='c#', author_id=au3.id)
bk5 = Book(name='ruby', author_id=au3.id)
db.session.add_all([bk1, bk2, bk3, bk4, bk5])
db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)
