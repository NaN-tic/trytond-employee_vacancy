# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
import activity
import vacancy

def register():
    Pool.register(
        activity.Activity,
        vacancy.Resume,
        vacancy.Vacancy,
        vacancy.VacancyURL,
        vacancy.CandidatePhase,
        vacancy.CandidateApplicationMethod,
        vacancy.Candidate,
        vacancy.EmployeeCardType,
        vacancy.ResumeCard,
        vacancy.EmployeeSkillType,
        vacancy.ResumeSkill,
        vacancy.ResumeLanguage,
        vacancy.EmployeeEducationLevel,
        vacancy.ResumeEducation,
        vacancy.ResumePosition,
        module='employee_vacancy', type_='model')
