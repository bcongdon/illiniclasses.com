cached_courses = []

def get_course_ids(mongo):
    global cached_courses
    if cached_courses:
        return cached_courses
    classes = []
    departments = mongo.db.collection_names()
    for dep in departments:
        for c in mongo.db[dep].find():
            classes.append(c.get('course_id', ''))
    cached_courses = classes
    return classes
