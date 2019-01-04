from django import template

register = template.Library()


@register.filter
def clr(obj, attr):
    score = obj[attr]
    mxr = 200
    mxg = 150
    return "rgba(" + str(round(mxr * (100 - score) / max(score, 100 - score))) + ", " + str(round(mxg * score / max(score, 100 - score))) + ", 0, 0.7)"

@register.filter
def sclr(obj, attr):
    score = obj[attr] * 10
    mxr = 150
    mxg = 100
    return "rgba(" + str(round(mxr * (100 - score) / max(score, 100 - score))) + ", " + str(round(mxg * score / max(score, 100 - score))) + ", 0, 0.7)"
