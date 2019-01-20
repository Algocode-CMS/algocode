function addCell(row, text, klass, rowSpan, colSpan) {
    let cell = row.insertCell();
    cell.innerHTML = text;
    cell.className = klass || '';
    cell.rowSpan = rowSpan || 1;
    cell.colSpan = colSpan || 1;
    return cell;
}

var loadFailed = function() {
    alert('Не удалось получить таблицу результатов!');
};

var compareUsers = function(a, b) {
    if (a['mark'] !== b['mark']) {
        return b['mark'] - a['mark'];
    }
    if (a['score'] !== b['score']) {
        return b['score'] - a['score'];
    }
    if (a['penalty'] !== b['penalty']) {
        return a['penalty'] - b['penalty'];
    }
    return a['name'].localeCompare(b['name']);
};

var getMarkColor = function(mark) {
    if (mark >= 7.5) {
        return 'lightgreen';
    } else if (mark >= 5.5) {
        return 'greenyellow';
    } else if (mark >= 3.5) {
        return 'yellow';
    } else {
        return 'lightcoral';
    }
};

var calculateMark = function(users, contests) {
    if (is_olymp) {
        let max_score = {};
        users.forEach(function(user) {
            let id = user['id'];
            contests.forEach(function(contest, idx) {
                let score = 0;
                contest['users'][id].forEach(function(result) {
                    score += result['score'];
                });
                if (idx in max_score) {
                    max_score[idx] = Math.max(max_score[idx], score);
                } else {
                    max_score[idx] = score;
                }
            });
        });
        users.forEach(function(user) {
            let id = user['id'];
            user['mark'] = 0.0;
            let sum_coef = 0.0;
            contests.forEach(function(contest, idx) {
                let score = 0;
                contest['users'][id].forEach(function(result) {
                    score += result['score'];
                });
                sum_coef += contest['coefficient'];
                if (max_score[idx] !== 0) {
                    user['mark'] += contest['coefficient'] * score / max_score[idx] * 10;
                }
            });
            if (sum_coef !== 0.0) {
                user['mark'] /= sum_coef;
            }
        });
    } else {
        users.forEach(function(user) {
            let id = user['id'];
            user['mark'] = 0.0;
            let sum_coef = 0.0;
            contests.forEach(function(contest) {
                let solved = 0;
                let problems = 0;
                contest['users'][id].forEach(function(result) {
                    if (result['verdict'] === 'OK') {
                        solved++;
                    }
                    problems++;
                });
                sum_coef += contest['coefficient'];
                if (problems !== 0) {
                    user['mark'] += contest['coefficient'] * Math.sqrt(solved / problems) * 10;
                }
            });
            if (sum_coef !== 0.0) {
                user['mark'] /= sum_coef;
            }
        });
    }
};

var calculateInformation = function(users, contests) {
    users.forEach(function(user) {
        let id = user['id'];
        user['score'] = 0.0;
        user['penalty'] = 0;
        contests.forEach(function(contest) {
            contest['users'][id].forEach(function(result) {
                user['score'] += result['score'];
                if (result['score'] !== 0) {
                    user['penalty'] += result['penalty'];
                }
            });
        });
    });
};

var getScoreColor = function(score) {
    let red = parseInt(240 + (144 - 240) * Math.sqrt(score / 100));
    let green = parseInt(128 + (238 - 128) * Math.sqrt(score / 100));
    let blue = parseInt(128 + (144 - 128) * Math.sqrt(score / 100));
    return 'rgba(' + red + ',' + green + ',' + blue + ')';
};

var addProblemCell = function(row, problem) {
    let score = problem['score'];
    let penalty = problem['penalty'];
    if (is_olymp) {
        let text;
        if (score === 100) {
            text = '100';
        } else {
            if (score === 0 && penalty === 0) {
                text = '';
            } else {
                text = score;
            }
        }
        let cell = addCell(row, text, 'gray');
        if (text !== '') {
            cell.style.backgroundColor = getScoreColor(score);
        }
    } else {
        const add_inf = function(text) {
            return '<p class="small">' + text + '&infin;</p>';
        };
        if (problem['verdict'] === 'OK') {
            let text = '+';
            if (penalty > 0) {
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text = add_inf(text);
                }
            }
            let cell = addCell(row, text, 'ok');
            if (penalty > 9) {
                cell.title = '+' + penalty;
            }
        } else {
            if (penalty === 0) {
                addCell(row, '', 'gray');
            } else {
                let text = '-';
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text = add_inf(text);
                }
                let cell = addCell(row, text, 'bad');
                if (penalty > 0) {
                    cell.title = '-' + penalty;
                }
            }
        }
    }
};

var addHeading = function(data, holder) {
    let header_row1 = holder.insertRow();
    let header_row2 = holder.insertRow();
    addCell(header_row1, 'Место', '', 2, 1);
    addCell(header_row1, 'Гр.', '', 2, 1);
    addCell(header_row1, 'Фамилия и имя', '', 2, 1);
    addCell(header_row1, (is_olymp ? 'Балл' : 'Решено'), '', 2, 1);
    if (!is_olymp) {
        addCell(header_row1, 'Штраф', '', 2, 1);
    }
    if (enable_marks) {
        addCell(header_row1, 'Оценка', '', 2, 1);
    }

    let contests = data['contests'];
    contests.forEach(function(contest, idx) {
        let problems = contest['problems'];
        let coefficient = contest['coefficient'];
        let title_text = contest['title'] + ' (' + coefficient.toString() + ')';
        let title;
        if (contest_id === -1) {
            title = '<a href="./' + idx + '/">' + title_text + '</a>';
        } else {
            title = title_text;
        }
        addCell(header_row1, title, 'gray', 1, problems.length);
        problems.forEach(function(problem) {
            let cell = addCell(header_row2, problem['short'], 'problem_letter gray');
            cell.title = problem['long'];
        });
    });
};

function fixColumnWidths(head, body) {
    let results_pos = head.childNodes[0].childNodes.length;
    head.childNodes[0].childNodes.forEach(function (column, idx) {
        if (column.classList.contains('gray')) {
            results_pos = Math.min(results_pos, idx);
        }
    });
    let max_width = {};
    [head, body].forEach(function(obj) {
        obj.childNodes.forEach(function(row, row_idx) {
            if (row_idx === 1) {
                return;
            }
            row.childNodes.forEach(function (column, idx) {
                if (idx >= results_pos) {
                    return;
                }
                let width = column.clientWidth;
                if (idx in max_width) {
                    max_width[idx] = Math.max(max_width[idx], width);
                } else {
                    max_width[idx] = width;
                }
            });
        });
    });
    [head, body].forEach(function(obj) {
        obj.childNodes.forEach(function(row, row_idx) {
            if (row_idx === 1) {
                return;
            }
            row.childNodes.forEach(function (column, idx) {
                if (idx >= results_pos) {
                    return;
                }
                column.style.minWidth = max_width[idx] + 'px';
            });
        });
    });
}

var buildStandings = function(data) {
    let contests = data['contests'];
    if (contest_id !== -1) {
        if (contest_id < 0 || contest_id >= contests.length) {
            alert('Wrong contest id!');
        }
        contests = [contests[contest_id]];
        data['contests'] = contests;
    }

    let table = document.getElementById('standings');
    let header = document.createElement('thead');
    let body = document.createElement('tbody');
    table.appendChild(header);
    table.appendChild(body);
    addHeading(data, header);
    addHeading(data, body);

    let users = data['users'];
    calculateInformation(users, contests);
    calculateMark(users, contests);
    users.sort(compareUsers);

    for (let i = 0; i < users.length; i++) {
        let user = users[i];
        let id = user['id'];
        let row = body.insertRow();
        addCell(row, i + 1);
        addCell(row, user['group_short']);
        addCell(row, user['name'], 'name');
        addCell(row, user['score']);
        if (!is_olymp) {
            addCell(row, user['penalty']);
        }
        if (enable_marks) {
            let cell = addCell(row, user['mark'].toFixed(2));
            cell.style.backgroundColor = getMarkColor(user['mark']);
        }

        contests.forEach(function (contest) {
            let problems = contest['users'][id];
            problems.forEach(function (problem) {
                addProblemCell(row, problem);
            });
        });
    }

    fixColumnWidths(header, body);
    document.getElementsByClassName('wrapper')[0].addEventListener('scroll', function(e) {
        header.style.marginLeft = -e.target.scrollLeft + 'px';
    });
};

document.addEventListener('DOMContentLoaded', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/standings_data/' + standings_id, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        let status = xhr.status;
        if (status === 200) {
            buildStandings(xhr.response);
        } else {
            loadFailed();
        }
    };
    xhr.send();
});
