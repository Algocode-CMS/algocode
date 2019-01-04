var olymp = 0;

var users = [];

function comp_sum(a, b) {
    if (a.score !== b.score) {
        return a.score > b.score
    }
    return a.penalty < b.penalty;
}

var contest_id;
function comp_contest(a, b) {
    if (a.contest_score[contest_id] !== b.contest_score[contest_id]) {
        return a.contest_score[contest_id] > b.contest_score[contest_id];
    }
    return a.contest_penalty[contest_id] < b.contest_penalty[contest_id];
}

var problem_id;
function comp_problem(a, b) {
    if (a.problem_score[contest_id][problem_id] !== b.problem_score[contest_id][problem_id]) {
        return a.problem_score[contest_id][problem_id] > b.problem_score[contest_id][problem_id];
    }
    return a.problem_penalty[contest_id][problem_id] < b.problem_penalty[contest_id][problem_id];
}

function sort_contest(c) {
    var i;

}