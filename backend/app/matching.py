def calculate_match_score(candidate_skills, required_skills):
    if not candidate_skills or not required_skills:
        return 0

    candidate_set = {
        skill.strip().lower()
        for skill in candidate_skills.split(",")
        if skill.strip()
    }

    required_set = {
        skill.strip().lower()
        for skill in required_skills.split(",")
        if skill.strip()
    }

    if not required_set:
        return 0

    matched_skills = candidate_set.intersection(required_set)

    score = (len(matched_skills) / len(required_set)) * 100

    return round(score)