import os
import random
from dateutil.relativedelta import relativedelta
from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.exceptions import UserError


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
        depends=['state', 'company'], domain=[
            ('company', '=', Eval('company')),
            ])
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
            'company': Eval('company'),
        }, depends=['company'])
    resume = fields.Many2One('employee.resume', 'Resume', domain=[
            ('party', '=', Eval('party')),
            ], depends=['party'])
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


class ImportCandidateLinkedInStart(ModelView):
    'Employee Candidate LinkedIn Import Start'
    __name__ = 'employee.candidate.linkedin.import.start'

    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)
    phase = fields.Many2One('employee.candidate.phase', 'Phase', required=True)
    application_method = fields.Many2One(
        'employee.candidate.application_method', 'Application Method')
    urls = fields.Text('Candidate URLs', required=True,
        help='Provide a list of candidate URLs separated by new lines')


class ImportCandidateLinkedInResult(ModelView):
    'Employee Candidate LinkedIn Import Result'
    __name__ = 'employee.candidate.linkedin.import.result'
    text = fields.Text('Text', readonly=True)


class ImportCandidateLinkedIn(Wizard):
    'Employee Candidate LinkedIn Import'
    __name__ = 'employee.candidate.linkedin.import'

    start_state = 'ask'
    ask = StateView('employee.candidate.linkedin.import.start',
        'employee_vacancy.linkedin_import_start_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Import", 'import_', 'tryton-launch', default=True),
            ])
    import_ = StateTransition()
    result = StateView('employee.candidate.linkedin.import.result',
            'employee_vacancy.linkedin_import_result_form', [
                Button('End', 'end', 'tryton-cancel'),
                ])


    def transition_import_(self):
        pool = Pool()
        Party = pool.get('party.party')
        ContactMechanism = pool.get('party.contact_mechanism')
        Candidate = pool.get('employee.candidate')
        Resume = pool.get('employee.resume')

        urls = self.ask.urls.split()
        profiles, failed = self.scrape_linkedin(self.ask.username,
                self.ask.password, urls)
        for profile in profiles:
            party = Party()
            party.name = profile['name']
            party.save()
            phone = ContactMechanism()
            phone.party = party
            phone.type = 'phone'
            phone.value = profile['phone']
            phone.save()
            email = ContactMechanism()
            email.party = party
            email.type = 'email'
            email.value = profile['email']
            email.save()
            resume = Resume()
            resume.party = party
            resume.url = profile['profile_url']
            resume.save()
            candidate = Candidate()
            candidate.vacancy = self.record
            candidate.party = party
            candidate.phase = self.ask.phase
            candidate.application_method = self.ask.application_method
            candidate.url = profile['application_url']
            candidate.save()

        if failed:
            self.result.text = '\n'.join(failed)
            return 'result'
        return 'end'

    def scrape_profile(self, page):
        name = page.locator("h1:has-text(' application')").inner_text()
        name = name.strip().split('’')[0]

        profile = page.locator('a:has-text("See full profile")').get_attribute('href')
        profile = profile.strip()

        more = page.locator("button:has-text('More…')").click()

        # Wait to ensure email and phone are loaded after the click
        page.wait_for_timeout(1000)
        text = page.content()

        # Wait some extra time to prevent bot detection
        page.wait_for_timeout(int(1000 * random.random()))

        email_pos = text.find('Email applicant at ')
        email = text[email_pos+len('Email applicant at '):].strip()
        email = email.split()[0].strip()

        phone_pos = text.find('Copy phone number')
        phone = text[phone_pos+len('Copy phone number'):].strip()
        phone = phone.split()[0].strip()
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'profile_url': 'https://linkedin.com' + profile,
            'application_url': page.url,
            }

    def scrape_login(self, page, username, password):
        # Wait just to so that LinkedIn does not recognize we're a bot
        page.locator('text=Sign in').click()
        page.locator('button:has-text("Accept")').click()
        page.locator('[aria-label="Email or Phone"]').fill(username)
        page.wait_for_timeout(500)
        page.locator('[aria-label="Password"]').fill(password)
        page.wait_for_timeout(500)
        page.locator('[aria-label="Sign in"]').click()
        page.wait_for_timeout(1500)


    def scrape_linkedin(self, username, password, urls):
        from playwright.sync_api import sync_playwright, TimeoutError

        first = True
        profiles = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless='DISPLAY' not in os.environ)
            page = browser.new_page()
            failed = []
            for url in urls:
                for retries in range(3):
                    try:
                        page.goto(url)
                        if first:
                            first = False
                            self.scrape_login(page, username, password)

                        profile = self.scrape_profile(page)
                        print('Profile:')
                        print(profile)
                        profiles.append(profile)
                        break
                    except TimeoutError:
                        pass
                else:
                    failed.append(url)
            browser.close()
        return profiles, failed
