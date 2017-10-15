from flask import Flask, render_template, make_response, request, redirect
import sqlite3

app = Flask(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/')
def main():
    conn = sqlite3.connect('leetcode.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(
        'SELECT lang,title,url,path FROM submission a WHERE EXISTS(SELECT 1 FROM submission b WHERE b.downloaded=1 AND b.removed=0 AND a.lang=b.lang AND a.title=b.title GROUP BY lang,title HAVING COUNT(lang)>1) ORDER BY lang,title')
    problems = c.fetchall()
    conn.close()
    return render_template('duplicate.html', problems=problems)


@app.route('/view/<path:path>')
def view(path=None):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    response = make_response(content)
    response.headers['content-type'] = 'text/plain'
    return response


@app.route('/remove', methods=['POST'])
def remove():
    url = request.form['url']
    conn = sqlite3.connect('leetcode.db')
    c = conn.cursor()
    c.execute('UPDATE submission SET removed=1 WHERE url=?', (url,))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
