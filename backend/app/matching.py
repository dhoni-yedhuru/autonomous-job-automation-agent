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


def analyze_match(candidate_skills, required_skills):
    candidate_set = {
        skill.strip().lower()
        for skill in (candidate_skills or "").split(",")
        if skill.strip()
    }

    required_set = {
        skill.strip().lower()
        for skill in (required_skills or "").split(",")
        if skill.strip()
    }

    matched_skills = sorted(candidate_set.intersection(required_set))
    missing_skills = sorted(required_set - candidate_set)

    score = 0

    if required_set:
        score = round(
            (len(matched_skills) / len(required_set)) * 100
        )

    return {
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }