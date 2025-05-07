from dateutil.relativedelta import relativedelta
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool


class Resume(ModelSQL, ModelView):
    'Resume'
    __name__ = 'employee.resume'
    party = fields.Many2One('party.party', 'Party', required=True)
    picture = fields.Binary('Picture')
    text = fields.Text('Text')
    url = fields.Char('URL')
    citizenship = fields.Many2One('country.country', 'Citizenship')
    gender = fields.Selection([
            (None, ''),
            ('m', 'Male'),
            ('f', 'Female'),
            ], 'Sex')
    birthdate = fields.Date('Birthdate')
    age = fields.Function(fields.Integer('Age'), 'on_change_with_age')
    cards = fields.One2Many('employee.resume.card', 'resume', 'Cards')
    skills = fields.One2Many('employee.resume.skill', 'resume', 'Skills')
    languages = fields.One2Many('employee.resume.language', 'resume',
        'Languages')
    educations = fields.One2Many('employee.resume.education', 'resume',
        'Education')
    positions = fields.One2Many('employee.resume.position', 'resume',
        'Positions')
    notes = fields.Text('Notes')

    def get_rec_name(self, name):
        return self.party.rec_name

    @fields.depends('birthdate')
    def on_change_with_age(self, name=None):
        Date = Pool().get('ir.date')
        if self.birthdate:
            return relativedelta(Date.today(), self.birthdate).years


class Vacancy(ModelSQL, ModelView):
    'Vacancy'
    __name__ = 'employee.vacancy'
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    company = fields.Many2One('company.company', 'Company', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True,
        domain=[('company', '=', Eval('company', -1))])
    start = fields.Date('Start')
    end = fields.Date('End')
    candidates = fields.One2Many('employee.candidate', 'vacancy',
        'Candidates')
    urls = fields.One2Many('employee.vacancy.url', 'vacancy', 'URLs')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('closed', 'Closed'),
            ], 'State')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_employee():
        User = Pool().get('res.user')

        if Transaction().context.get('employee'):
            return Transaction().context['employee']
        else:
            user = User(Transaction().user)
            if user.employee:
                return user.employee.id


class VacancyURL(ModelSQL, ModelView):
    'Vacancy URL'
    __name__ = 'employee.vacancy.url'
    _rec_name = 'url'
    vacancy = fields.Many2One('employee.vacancy', 'Vacancy', required=True)
    url = fields.Char('URL', required=True)


class CandidatePhase(ModelSQL, ModelView):
    'Candidate Phase'
    __name__ = 'employee.candidate.phase'
    name = fields.Char('Name', required=True)
    final = fields.Boolean('Final', help='A final phase, indicates that the '
        'candidature phase is not expected to be updated any more. Ie. '
        '"Rejected", "Contracted", etc.')


class CandidateApplicationMethod(ModelSQL, ModelView):
    'Candidate Application Method'
    __name__ = 'employee.candidate.application_method'
    name = fields.Char('Name', required=True)


class Candidate(ModelSQL, ModelView):
    'Candidate'
    __name__ = 'employee.candidate'
    sequence = fields.Integer('Sequence')
    company = fields.Function(fields.Many2One('company.company', 'Company'),
        'get_company', searcher='search_company')
    vacancy = fields.Many2One('employee.vacancy', 'Vacancy', required=True,
        ondelete='CASCADE')
    party = fields.Many2One('party.party', 'Party', required=True,
        context={
            'company': Eval('company', -1),
        }, depends=['company'])
    resume = fields.Many2One('employee.resume', 'Resume', domain=[
            ('party', '=', Eval('party')),
            ])
    application_method = fields.Many2One(
        'employee.candidate.application_method', 'Application Method')
    url = fields.Char('URL')
    application_date = fields.Date('Application Date')
    qualification = fields.Float('Qualification', digits=(16, 2))
    phase = fields.Many2One('employee.candidate.phase', 'Phase', required=True)
    notes = fields.Text('Notes')
    activities = fields.One2Many('activity.activity', 'resource', 'Activities',
        context={
            'vacancy_party': Eval('party'),
            }, depends=['party'])

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('party.rec_name',) + tuple(clause[1:])]

    @fields.depends('party')
    def on_change_with_resume(self):
        Resume = Pool().get('employee.resume')
        if not self.party:
            return
        resumes = Resume.search([
                ('party', '=', self.party.id)
                ])
        if resumes:
            return resumes[0].id

    @fields.depends('resume')
    def on_change_resume(self):
        if self.resume:
            self.party = self.resume.party

    def get_company(self, name):
        return self.vacancy.company.id

    @classmethod
    def search_company(cls, name, clause):
        return [('vacancy.%s' % name,) + tuple(clause[1:])]


class EmployeeCardType(ModelSQL, ModelView):
    'Employee Card Type'
    __name__ = 'employee.card.type'
    name = fields.Char('Name', required=True)


class ResumeCard(ModelSQL, ModelView):
    'Resume Card'
    __name__ = 'employee.resume.card'
    resume = fields.Many2One('employee.resume', 'Resume', required=True)
    card = fields.Many2One('employee.card.type', 'Card', required=True)
    identifier = fields.Char('Identifier')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')


class EmployeeSkillType(ModelSQL, ModelView):
    'Employee Skill Type'
    __name__ = 'employee.skill.type'
    name = fields.Char('Name', required=True)


class ResumeSkill(ModelSQL, ModelView):
    'Resume Skill'
    __name__ = 'employee.resume.skill'
    resume = fields.Many2One('employee.resume', 'Resume', required=True)
    skill = fields.Many2One('employee.skill.type', 'Skill', required=True)
    years = fields.Integer('Years of experience')
    notes = fields.Text('Notes')


class ResumeLanguage(ModelSQL, ModelView):
    'Resume Language'
    __name__ = 'employee.resume.language'
    resume = fields.Many2One('employee.resume', 'Resume', required=True)
    language = fields.Many2One('ir.lang', 'Language', required=True)
    fluency = fields.Selection([
            ('poor', 'Poor'),
            ('basic', 'Basic'),
            ('good', 'Good'),
            ('mother-tongue', 'Mother Tongue'),
            ], 'Fluency', required=True)
    skill = fields.Selection([
            (None, ''),
            ('writing', 'Writing'),
            ('reading', 'Reading'),
            ('speaking', 'Speaking'),
            ], 'Skill')
    notes = fields.Text('Notes')


class EmployeeEducationLevel(ModelSQL, ModelView):
    'Employee Education Level'
    __name__ = 'employee.education.level'
    name = fields.Char('Name', required=True)


class ResumeEducation(ModelSQL, ModelView):
    'Resume Education'
    __name__ = 'employee.resume.education'
    resume = fields.Many2One('employee.resume', 'Resume', required=True)
    level = fields.Many2One('employee.education.level', 'Level', required=True)
    school = fields.Many2One('party.party', 'School')
    degree = fields.Char('Degree')
    field = fields.Char('Field of study')
    start_year = fields.Integer('Start Year')
    end_year = fields.Integer('End Year')
    description = fields.Text('Description')


class ResumePosition(ModelSQL, ModelView):
    'Resume Position'
    __name__ = 'employee.resume.position'
    resume = fields.Many2One('employee.resume', 'Resume', required=True)
    organization = fields.Char('Organization')
    title = fields.Char('Title')
    description = fields.Text('Description')
    start = fields.Date('Start')
    end = fields.Date('End')
    location = fields.Char('Location')
