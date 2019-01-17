function addCell(row, text, klass, rowSpan, colSpan) {
    var cell = row.insertCell();
    cell.innerHTML = text;
    cell.className = klass || '';
    cell.rowSpan = rowSpan || 1;
    cell.colSpan = colSpan || 1;
    return cell;
}

var is_olymp = false;
var enable_marks = true;

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
        return b['penalty'] - a['penalty'];
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
        var max_score = {};
        users.forEach(function(user) {
            var id = user['id'];
            contests.forEach(function(contest, idx) {
                var score = 0;
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
            var id = user['id'];
            user['mark'] = 0.0;
            contests.forEach(function(contest, idx) {
                var score = 0;
                contest['users'][id].forEach(function(result) {
                    score += result['score'];
                });
                if (max_score[idx] !== 0) {
                    user['mark'] += score / max_score[idx] * 10;
                }
            });
            if (contests.length !== 0) {
                user['mark'] /= contests.length;
            }
        });
    } else {
        users.forEach(function(user) {
            var id = user['id'];
            user['mark'] = 0.0;
            contests.forEach(function(contest) {
                var solved = 0;
                var problems = 0;
                contest['users'][id].forEach(function(result) {
                    if (result['verdict'] === 'OK') {
                        solved++;
                    }
                    problems++;
                });
                if (problems !== 0) {
                    user['mark'] += Math.sqrt(solved / problems) * 10;
                }
            });
            if (contests.length !== 0) {
                user['mark'] /= contests.length;
            }
        });
    }
};

var calculateInformation = function(users, contests) {
    users.forEach(function(user) {
        var id = user['id'];
        user['score'] = 0.0;
        user['penalty'] = 0;
        contests.forEach(function(contest) {
            contest['users'][id].forEach(function(result) {
                user['score'] += result['score'];
                user['penalty'] += result['penalty'];
            });
        });
    });
};

var getScoreColor = function(score) {
    var red = parseInt(240 + (144 - 240) * Math.sqrt(score / 100));
    var green = parseInt(128 + (238 - 128) * Math.sqrt(score / 100));
    var blue = parseInt(128 + (144 - 128) * Math.sqrt(score / 100));
    return 'rgba(' + red + ',' + green + ',' + blue + ')';
};

var addProblemCell = function(row, problem) {
    var score = problem['score'];
    var penalty = problem['penalty'];
    if (is_olymp) {
        var text;
        if (score === 100) {
            text = '<p class="small">100</p>';
        } else {
            if (score === 0 && penalty === 0) {
                text = '';
            } else {
                text = score;
            }
        }
        var cell = addCell(row, text, 'gray');
        if (text !== '') {
            cell.style.backgroundColor = getScoreColor(score);
        }
    } else {
        if (problem['verdict'] === 'OK') {
            var text = '+';
            if (penalty > 0) {
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text += '&#8734;';
                }
            }
            var cell = addCell(row, text, 'ok');
            if (penalty > 9) {
                cell.title = '+' + penalty;
            }
        } else {
            if (penalty === 0) {
                addCell(row, '', 'gray');
            } else {
                var text = '-';
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text += '&infin;';
                }
                var cell = addCell(row, text, 'bad');
                if (penalty > 0) {
                    cell.title = '-' + penalty;
                }
            }
        }
    }
};

var addHeading = function(data, holder) {
    var header_row1 = holder.insertRow();
    var header_row2 = holder.insertRow();
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

    var contests = data['contests'];
    contests.forEach(function(contest, idx) {
        var problems = contest['problems'];
        var title;
        if (contest_id === -1) {
            title = '<a href="./' + idx + '/">' + contest['title'] + '</a>';
        } else {
            title = contest['title'];
        }
        addCell(header_row1, title, 'gray', 1, problems.length);
        problems.forEach(function(problem) {
            var cell = addCell(header_row2, problem['short'], 'problem_letter gray');
            cell.title = problem['long'];
        });
    });
};

function fixColumnWidths(head, body) {
    var results_pos = head.childNodes[0].childNodes.length;
    head.childNodes[0].childNodes.forEach(function (column, idx) {
        if (column.classList.contains('gray')) {
            results_pos = Math.min(results_pos, idx);
        }
    });
    var max_width = {};
    [head, body].forEach(function(obj) {
        obj.childNodes.forEach(function(row, row_idx) {
            if (row_idx === 1) {
                return;
            }
            row.childNodes.forEach(function (column, idx) {
                if (idx >= results_pos) {
                    return;
                }
                var width = column.clientWidth;
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
    var contests = data['contests'];
    if (contest_id !== -1) {
        if (contest_id < 0 || contest_id >= contests.length) {
            alert('Wrong contest id!');
        }
        contests = [contests[contest_id]];
        data['contests'] = contests;
    }

    var table = document.getElementById('standings');
    var header = document.createElement('thead');
    var body = document.createElement('tbody');
    table.appendChild(header);
    table.appendChild(body);
    addHeading(data, header);
    addHeading(data, body);

    var users = data['users'];
    calculateInformation(users, contests);
    calculateMark(users, contests);
    users.sort(compareUsers);

    for (var j = 0; j < 30; j++) {
        for (var i = 0; i < users.length; i++) {
            var user = users[i];
            var id = user['id'];
            var row = body.insertRow();
            addCell(row, i + 1);
            addCell(row, user['group_short']);
            addCell(row, user['name'], 'name');
            addCell(row, user['score']);
            if (!is_olymp) {
                addCell(row, user['penalty']);
            }
            if (enable_marks) {
                var cell = addCell(row, user['mark'].toFixed(2));
                cell.style.backgroundColor = getMarkColor(user['mark']);
            }

            contests.forEach(function (contest) {
                var problems = contest['users'][id];
                problems.forEach(function (problem) {
                    addProblemCell(row, problem);
                });
            });
        }
    }

    fixColumnWidths(header, body);
    document.getElementsByClassName('wrapper')[0].addEventListener('scroll', function(e) {
        header.style.marginLeft = -e.target.scrollLeft + 'px';
    });
};

document.addEventListener('DOMContentLoaded', function () {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/standings_data/' + standings_id, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        var status = xhr.status;
        if (status === 200) {
            buildStandings(xhr.response);
        } else {
            loadFailed();
        }
    };
    xhr.send();
});
