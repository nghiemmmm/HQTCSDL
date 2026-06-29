import re

with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace hasDuplicateAnswers
old_func = """function hasDuplicateAnswers(question) {
    const answers = [
      normalizeAnswerText(question.a),
      normalizeAnswerText(question.b),
      normalizeAnswerText(question.c),
      normalizeAnswerText(question.d)
    ];
    return new Set(answers).size !== answers.length;
  }"""

new_func = """function checkDuplicateAnswers(question) {
    const a = normalizeAnswerText(question.a);
    const b = normalizeAnswerText(question.b);
    const c = normalizeAnswerText(question.c);
    const d = normalizeAnswerText(question.d);

    if (a === b) return "Đáp án A trùng đáp án B";
    if (a === c) return "Đáp án A trùng đáp án C";
    if (a === d) return "Đáp án A trùng đáp án D";
    if (b === c) return "Đáp án B trùng đáp án C";
    if (b === d) return "Đáp án B trùng đáp án D";
    if (c === d) return "Đáp án C trùng đáp án D";

    return null;
  }"""

if old_func in js:
    js = js.replace(old_func, new_func)
else:
    # Use regex
    js = re.sub(r'function hasDuplicateAnswers[\s\S]*?\}', new_func, js)

# Replace the check in ghi()
old_check = """if (hasDuplicateAnswers(obj)) return showError("Bốn đáp án A, B, C, D không được trùng nội dung.");"""
# Sometimes it's encoded or has different whitespace, so let's use regex
js = re.sub(r'if \(hasDuplicateAnswers\(obj\)\) return showError\([^)]+\);', 'const duplicateError = checkDuplicateAnswers(obj);\n    if (duplicateError) return showError(duplicateError);', js)

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=11', html)
with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
    f.write(html)
