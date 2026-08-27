"""
Email templates for the PivotPaper resume writing service cold outreach.

Templates are organized by segment and email number (1-4).
Each template returns a dict with 'subject' and 'body' keys.
All templates support {first_name} personalization.
"""


def get_template(segment: str, email_number: int) -> dict:
    """
    Retrieve the email template for a given segment and email number.

    Args:
        segment: One of 'open_to_work', 'career_changer', 'recent_grad', 'mid_career', 'laid_off'
        email_number: 1 through 4

    Returns:
        dict with 'subject' and 'body' keys
    """
    templates = {
        "open_to_work": {
            1: {
                "subject": "{first_name}, your resume might be holding you back",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>I noticed you're actively looking for new opportunities — congrats on taking that step. The job market is competitive right now, and I've seen talented people get overlooked simply because their resume doesn't pass ATS filters or grab a recruiter's attention in the first 6 seconds.</p>\n\n<p>At <strong>PivotPaper</strong>, we specialize in crafting resumes that actually land interviews. Our clients typically see a <strong>3x increase in callback rates</strong> within the first two weeks.</p>\n\n<p>Would it be helpful if I did a quick (free) audit of your current resume and showed you where the gaps are?</p>\n\n<p>No pressure either way — just trying to help.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            2: {
                "subject": "Re: Quick resume tip for your search, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Just circling back — I wanted to share something that might help your search right now.</p>\n\n<p>One of the biggest mistakes I see on resumes from active job seekers: <strong>listing responsibilities instead of results</strong>. Recruiters skim for impact metrics. If your bullets don't start with numbers or outcomes, you're leaving interviews on the table.</p>\n\n<p>Here's a quick example:<br>\n❌ \"Managed a team of 5 engineers\"<br>\n✅ \"Led 5-person engineering team that shipped 3 products ahead of schedule, generating $2M ARR\"</p>\n\n<p>If you'd like us to rewrite your resume with this approach, we're offering a <strong>free 15-minute consultation</strong> this week.</p>\n\n<p>Interested?</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            3: {
                "subject": "This helped a job seeker land 4 interviews in one week",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Wanted to share a quick win from one of our recent clients — Sarah was applying to 20+ jobs a week with zero callbacks. After we rebuilt her resume:</p>\n\n<ul>\n<li>4 interview requests in the first week</li>\n<li>2 offers within 3 weeks</li>\n<li>$15K salary bump from her previous role</li>\n</ul>\n\n<p>The difference? We restructured her experience around <strong>quantifiable achievements</strong> and optimized every section for ATS compatibility.</p>\n\n<p>I put together a free guide: <em>\"5 Resume Fixes That Get Callbacks\"</em> — happy to send it over if you're interested.</p>\n\n<p>Just reply \"send it\" and it's yours.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            4: {
                "subject": "Last note from me, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>I don't want to clutter your inbox, so this will be my last email.</p>\n\n<p>If you ever want a professional set of eyes on your resume — whether that's now or 6 months from now — we're here. No hard sell, just good work.</p>\n\n<p>Wishing you the best in your search. You've got this. 💪</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
        },
        "career_changer": {
            1: {
                "subject": "{first_name}, pivoting careers? Your resume needs a different strategy",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Career transitions are exciting — but they come with a unique resume challenge. When you're switching industries, a traditional chronological resume can actually work against you by highlighting the \"wrong\" experience.</p>\n\n<p>At <strong>PivotPaper</strong>, we specialize in helping career changers reframe their background. We highlight <strong>transferable skills and relevant achievements</strong> so hiring managers see your potential, not just your past titles.</p>\n\n<p>Would you be open to a quick chat about how to position your experience for the roles you're targeting?</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            2: {
                "subject": "Re: The #1 resume mistake career changers make",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Quick follow-up with a tip that's helped dozens of our career-changer clients:</p>\n\n<p><strong>Stop leading with your job titles.</strong> When you're pivoting, titles from your old industry can trigger instant \"not a fit\" reactions from recruiters.</p>\n\n<p>Instead, lead with a <strong>Skills-Based Summary</strong> that maps your experience to the new role's requirements. We call it the \"bridge section\" — it answers the recruiter's #1 question: \"Why should I consider this person?\"</p>\n\n<p>Want me to show you what this looks like for your specific transition? Happy to do a free 10-minute teardown.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            3: {
                "subject": "From teacher to tech PM — how Marcus did it",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Quick story that might resonate: Marcus came to us after 8 years in education, wanting to break into product management. His resume screamed \"teacher\" — and he'd been rejected 30+ times.</p>\n\n<p>We restructured his resume to lead with:</p>\n<ul>\n<li>Curriculum design → Product roadmapping</li>\n<li>Student outcome metrics → Data-driven decision making</li>\n<li>Cross-department collaboration → Stakeholder management</li>\n</ul>\n\n<p>Result: <strong>3 PM interviews in 2 weeks</strong>, offer within a month.</p>\n\n<p>The skills were always there — we just translated them into the right language.</p>\n\n<p>If you're navigating a similar pivot, I'd love to help. Reply and let's talk.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            4: {
                "subject": "Signing off, {first_name} — one last thought",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>This is my last note. I know career changes are stressful enough without extra emails.</p>\n\n<p>Just remember: your experience isn't a liability — it's a differentiator. The right resume makes that clear to hiring managers.</p>\n\n<p>Whenever you're ready to make the pivot official, we're here to help you tell that story. No expiration date on this offer.</p>\n\n<p>Rooting for you.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
        },
        "recent_grad": {
            1: {
                "subject": "{first_name}, graduating into this job market? Let's talk strategy",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>First off — congrats on graduating! Now comes the hard part: standing out in a job market where entry-level roles get 200+ applications.</p>\n\n<p>Here's what most new grads don't realize: <strong>your resume format matters more than your GPA</strong>. Recruiters spend an average of 6 seconds on a first pass. If your layout, structure, and keywords aren't optimized, your degree alone won't save you.</p>\n\n<p>At <strong>PivotPaper</strong>, we help recent graduates turn internships, projects, and coursework into compelling professional narratives that compete with experienced candidates.</p>\n\n<p>Want a free resume review? I'll tell you exactly what's working and what needs to change.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            2: {
                "subject": "Re: How to compete with experienced candidates, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>One more thought for you — the biggest advantage new grads have (that most waste):</p>\n\n<p><strong>Projects and coursework are fair game.</strong> But you have to present them like professional work, not homework.</p>\n\n<p>Instead of:<br>\n❌ \"Completed senior capstone project on machine learning\"</p>\n\n<p>Try:<br>\n✅ \"Built ML classification model achieving 94% accuracy on 10K-record dataset; presented findings to faculty panel of 5\"</p>\n\n<p>See the difference? One sounds like a student. The other sounds like a professional.</p>\n\n<p>We do this transformation for every bullet on your resume. Interested in seeing what yours could look like?</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            3: {
                "subject": "She had zero work experience and still landed a FAANG interview",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Real story: Priya graduated with a CS degree, no internships, no work experience. She was convinced she'd need to \"pay her dues\" at a small company first.</p>\n\n<p>We rebuilt her resume around:</p>\n<ul>\n<li>Open-source contributions (framed as collaborative engineering)</li>\n<li>Hackathon wins (framed as rapid prototyping under pressure)</li>\n<li>TA experience (framed as technical mentorship)</li>\n</ul>\n\n<p>She landed interviews at <strong>two FAANG companies</strong> within a month.</p>\n\n<p>The experience was always there — it just needed the right framing. That's what we do.</p>\n\n<p>Want to explore what's possible with your background? Just reply.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            4: {
                "subject": "Last one from me, {first_name} — go crush it",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>I'll stop filling your inbox. Just know: being a recent grad isn't a disadvantage — it's a blank canvas. The right resume tells your story before you even walk into the room.</p>\n\n<p>Whenever you're ready to level up your application materials, we're one reply away.</p>\n\n<p>Go get 'em. 🚀</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
        },
        "mid_career": {
            1: {
                "subject": "{first_name}, is your resume keeping up with your career growth?",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>After several years in your field, your resume should be doing heavy lifting for you — opening doors to senior roles, leadership positions, and better compensation.</p>\n\n<p>But here's what we see constantly: <strong>experienced professionals underselling themselves</strong> with resumes that read like job descriptions instead of impact statements.</p>\n\n<p>At <strong>PivotPaper</strong>, we work with mid-career professionals to reposition their experience for the next level. Whether that's a director role, a VP title, or a strategic lateral move — your resume needs to tell that story.</p>\n\n<p>Would a free resume audit be useful? I'll show you exactly where you're leaving value on the table.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            2: {
                "subject": "Re: The resume gap between senior ICs and directors",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Quick insight from working with hundreds of mid-career professionals:</p>\n\n<p>The #1 difference between a resume that gets you <em>another lateral role</em> vs. one that gets you <em>promoted</em>? <strong>Scope language.</strong></p>\n\n<p>Senior IC resumes say: \"Delivered project X on time and under budget\"<br>\nDirector-level resumes say: \"Defined and executed product strategy across 3 business units, driving $8M revenue growth\"</p>\n\n<p>If you're aiming up, your resume needs to speak the language of the level above you — not document what you do today.</p>\n\n<p>Want us to assess where your resume falls on this spectrum? Free, no strings.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            3: {
                "subject": "How a VP candidate went from ghosted to 3 competing offers",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>James had 12 years of experience and was targeting VP of Engineering roles. Despite his track record, he kept getting ghosted after submitting applications.</p>\n\n<p>The problem? His resume was 3 pages of tactical details. It read like a senior engineer's resume, not an executive's.</p>\n\n<p>We rebuilt it with:</p>\n<ul>\n<li>Executive summary highlighting P&L impact</li>\n<li>Leadership narrative (team building, org design)</li>\n<li>Strategic outcomes over tactical execution</li>\n</ul>\n\n<p>Result: <strong>3 competing offers within 6 weeks</strong>, all at the VP level.</p>\n\n<p>If you're ready to position yourself for the next level, let's talk.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            4: {
                "subject": "Final note, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Last email from me. Your career speaks for itself — but your resume should amplify it, not diminish it.</p>\n\n<p>Whenever you're ready for your next move and want a resume that matches your ambition, we're here.</p>\n\n<p>Keep building great things.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
        },
        "laid_off": {
            1: {
                "subject": "{first_name}, navigating a layoff? Here's how to land faster",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>I know this isn't easy. Layoffs are disruptive no matter how talented you are — and they often have nothing to do with your performance.</p>\n\n<p>Here's the good news: companies are actively hiring people with your experience right now. The key is moving fast with the <strong>right materials</strong>.</p>\n\n<p>At <strong>PivotPaper</strong>, we work with professionals in transition to:</p>\n<ul>\n<li>Rebuild resumes that emphasize impact (not just the company name)</li>\n<li>Optimize for ATS filters in your target roles</li>\n<li>Position the transition as a strength, not a gap</li>\n</ul>\n\n<p>We're offering <strong>priority turnaround</strong> for people currently in transition. Want a free resume assessment?</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            2: {
                "subject": "Re: Quick tip for your job search, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>One thing I've noticed helping people through layoffs: <strong>don't let your resume tell the story of your last company — tell the story of your impact.</strong></p>\n\n<p>When a well-known company does layoffs, recruiters sometimes associate candidates with \"the struggling company.\" Combat this by:</p>\n\n<ol>\n<li>Leading with achievements, not company names</li>\n<li>Quantifying your personal contributions separate from team/company metrics</li>\n<li>Adding a brief \"Selected Accomplishments\" section at the top</li>\n</ol>\n\n<p>This reframes the narrative from \"laid off from Company X\" to \"high-impact professional available now.\"</p>\n\n<p>Want us to help you build this narrative? Free consultation, no commitment.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            3: {
                "subject": "From layoff to $30K raise — how Jen did it in 4 weeks",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Jen was laid off from a Series C startup in January. She was devastated — she'd been there 4 years and poured her heart into the product.</p>\n\n<p>We worked with her to:</p>\n<ul>\n<li>Extract and quantify her individual impact (separate from the failed company narrative)</li>\n<li>Rewrite her LinkedIn and resume to signal \"available and exceptional\"</li>\n<li>Target roles that valued her specific skill combination</li>\n</ul>\n\n<p>Result: <strong>New role in 4 weeks with a $30K salary increase.</strong> The layoff became the best thing that happened to her career.</p>\n\n<p>Your story can have the same ending. Reply if you'd like to explore how.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
            4: {
                "subject": "Rooting for you, {first_name}",
                "body": """<html><body>\n<p>Hi {first_name},</p>\n\n<p>Last note from me. I know the inbox is the last place you need more noise right now.</p>\n\n<p>Just remember: a layoff is a data point, not a verdict. The market still needs what you bring. When you're ready to put your best foot forward, we'll be here to help make that happen.</p>\n\n<p>Wishing you a fast and rewarding landing.</p>\n\n<p>Best,<br>\nThe PivotPaper Team<br>\n<a href=\"https://pivotpaper.us\">pivotpaper.us</a></p>\n</body></html>""",
            },
        },
    }

    if segment not in templates:
        raise ValueError(f"Unknown segment: {segment}. Valid: {list(templates.keys())}")
    if email_number not in templates[segment]:
        raise ValueError(f"Unknown email_number: {email_number}. Valid: 1-4")

    return templates[segment][email_number]


# Convenience: list valid segments
VALID_SEGMENTS = ["open_to_work", "career_changer", "recent_grad", "mid_career", "laid_off"]
