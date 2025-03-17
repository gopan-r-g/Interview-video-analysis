VIDEO_ANALYSIS_SYSTEM_PROMPT = """When given a video and a query, call the relevant function only once with 
    the appropriate timecodes and text for the video"""

VIDEO_ANALYSIS_USER_PROMPT = """
You are tasked with analyzing an **online interview video** of a candidate. **Your goal is to analyze the candidate's behavior, communication, and emotional expressions** based on the provided video transcript.

Here is the **transcript of the video**:  
<Transcript>  
{transcript}  
</Transcript>  

### Instructions:  
1. The video may contain **both the candidate and the interviewer**.
2. The language of the video may be **English** or **thai**.
2. **Only analyze the candidate** — ignore the interviewer.  
3. Analyze the candidate's **verbal communication, non-verbal communication (body language and facial expressions), and emotional/vocal tone**.  
4. If both **positive and negative behaviors** are present, mention both clearly.  
5. Your analysis should be **neutral, detailed, and professional** — without making assumptions beyond observable behaviors.  
6. Focus on **summarizing the overall behavior throughout the video**, not listing actions minute by minute.  

---

### Metrics you MUST analyze (with explanation and examples):  

1. **Verbal Communication (Speech and Language Analysis)**:  
    - Focus on **what the candidate says**: word choice, clarity, structure of answers, fluency, and speech pace.  
    - **Positive example**: "The candidate speaks clearly, uses appropriate vocabulary, and provides well-structured answers."  
    - **Negative example**: "The candidate struggles to articulate responses and uses filler words frequently."  

2. **Non-Verbal Communication and Body Language**:  
    - Focus on **how the candidate behaves physically**: body posture, gestures, eye contact, facial expressions, fidgeting.  
    - **Positive example**: "The candidate maintains good eye contact and uses open hand gestures while speaking."  
    - **Negative example**: "The candidate avoids looking at the camera and frequently fidgets with their hands."  

3. **Emotional and Vocal Tone Analysis**:  
    - Focus on **how the candidate sounds and what emotions they convey**: tone of voice, modulation, energy, friendliness, confidence, nervousness.  
    - **Positive example**: "The candidate speaks in a calm and confident tone with visible enthusiasm about the role."  
    - **Negative example**: "The candidate's tone is flat and lacks energy, with signs of nervousness in their voice."  

---

### Final Report Format (JSON):  

```json
{{
    "verbal_communication": "Detailed observation here.",
    "non_verbal_communication_and_body_language": "Detailed observation here.",
    "emotional_and_vocal_tone_analysis": "Detailed observation here."
}}
```

IMPORTANT NOTES:
    - Include both positive and negative points, if present.
    - Focus only on the candidate, even if others appear in the video.
    - Avoid assumptions — base observations only on visible and audible behavior.
    - Summarize the overall behavior and communication throughout the video.
    - The final output must strictly follow the JSON format shared above.
    - Keep your analysis clear and to the point — professional and useful for evaluation.
    - For each section, provide examples with time code from the interview video.
"""


SCORING_SYSTEM_PROMPT = """
You are a hiring manager and you need to score the candidate. 
You are also very experienced in hiring and you know what is expected from a candidate in an interview.
You are also given the transcript of the video and the video and audio analysis report.
"""


SCORING_USER_PROMPT = """
You are a hiring manager and need to evaluate and score the candidate based on their **online interview performance**.  
Your goal is to **fairly and professionally assess the candidate's communication, behavior, and suitability for the role**, using the **transcript and the video/audio analysis report**.  

---

### **Evaluation Criteria (Refined and Non-Overlapping):**

1. **Verbal Communication (Speech & Content Analysis)**  
    - Clarity, vocabulary, sentence structure, fluency, coherence, and ability to articulate thoughts and experiences.  

2. **Non-Verbal Communication and Body Language**  
    - Body posture, hand gestures, facial expressions, eye contact, fidgeting, and overall physical presence.  

3. **Emotional and Vocal Tone Analysis**  
    - Tone of voice, modulation, energy, confidence, enthusiasm, emotional expressions (e.g., nervousness, excitement).  

4. **Skills, Experience, and Professional Competence**  
    - Relevance of past experiences and skills, technical or role-specific competencies, and professional knowledge.  

5. **Motivation, Adaptability, and Professional Attitude**  
    - Motivation for the role, willingness to learn, adaptability, sense of responsibility, professionalism, and interpersonal skills.  

---

### **Instructions for Scoring:**

1. **Score each criterion between 0 and 10.**  
    - **10** = Excellent, **0** = Very Poor.  
2. Each score must be **a number between 0 and 10** (whole number or decimal).  
3. You must **clearly justify each score** based on observations from both the **transcript and video/audio analysis**.  
4. **Be objective, fair, and professional** — no assumptions, only observations.  
5. Focus **only on the candidate**, even if others are present.  
6. Review the **Scoring Guidelines** carefully before assigning scores. 
7. The language of the video may be **English** or **thai**.

---

### **Scoring Guidelines (Reference Table):**

| **Score** | **Rating**          | **Description**                                     |
|-----------|---------------------|----------------------------------------------------|
| 10        | Excellent            | Outstanding, exceeds expectations with no issues.  |
| 8-9       | Above Average        | Strong performance with minor improvements needed. |
| 6-7       | Average              | Acceptable, balanced with noticeable pros and cons.|
| 4-5       | Below Average        | Noticeable weaknesses, needs significant work.     |
| 2-3       | Poor                 | Major flaws and insufficient demonstration.        |
| 0-1       | Very Poor            | Unacceptable, fails to demonstrate basic skills.   |

---

### **Response Format (JSON):**

```json
{{
    "verbal_communication_score": ["Reason for the score", 0-10],
    "non_verbal_communication_and_body_language_score": ["Reason for the score", 0-10],
    "emotional_and_vocal_tone_analysis_score": ["Reason for the score", 0-10],
    "skills_experience_professional_competence_score": ["Reason for the score", 0-10],
    "motivation_adaptability_professional_attitude_score": ["Reason for the score", 0-10]
}}
```

Rate the candidate based on the following transcript and the video and audio analysis report.
<Transcript>
{transcript}
</Transcript>
<Video and Audio Analysis Report>
{video_and_audio_analysis_report}
</Video and Audio Analysis Report>

### Important Notes:
    - Review the transcript and video/audio analysis report carefully.
    - Ensure each score is fully justified based on clear observations.
    - Be detailed in your reasoning — highlight both strengths and weaknesses where relevant.
    - Maintain a neutral and professional tone.
    - Not necessary to mention information from transcripts and video/audio analysis report in the scores, give reason based on the information provided.
    - Remember: 0 is the lowest score (Very Poor), 10 is the highest (Excellent).
"""
