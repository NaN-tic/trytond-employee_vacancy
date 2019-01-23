======================
Party Replace Scenario
======================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date(2015, 1, 1)

Install asset_maintenance::

    >>> config = activate_modules('employee_vacancy')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create a party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Customer')
    >>> party.save()
    >>> party2 = Party(name='Customer')
    >>> party2.save()

Create an employee::

    >>> Employee = Model.get('company.employee')
    >>> employee = Employee()
    >>> employee.party = party
    >>> employee.company = company
    >>> employee.save()

Create a phase::

    >>> CandidatePhase = Model.get('employee.candidate.phase')
    >>> phase = CandidatePhase()
    >>> phase.name = 'Phase'
    >>> phase.save()

Create vacancy::

    >>> Vacancy = Model.get('employee.vacancy')
    >>> vacancy = Vacancy()
    >>> vacancy.name = 'Vacancy'
    >>> vacancy.employee = employee
    >>> vacancy.text = 'We have a vacancy.'
    >>> vacancy.start = datetime.date.today() - relativedelta(days=15)
    >>> vacancy.end = datetime.date.today()
    >>> vacancy.save()

Create a candidate::

    >>> Candidate = Model.get('employee.candidate')
    >>> candidate = Candidate()
    >>> candidate.vacancy = vacancy
    >>> candidate.party = party
    >>> candidate.phase = phase
    >>> candidate.save()

Create resume::

    >>> Resume = Model.get('employee.resume')
    >>> resume = Resume()
    >>> resume.party = party
    >>> resume.save()

Create level::

    >>> Level = Model.get('employee.education.level')
    >>> level = Level()
    >>> level.name = 'Level'
    >>> level.save()

Create resume education::

    >>> ResumeEducation = Model.get('employee.resume.education')
    >>> education = ResumeEducation()
    >>> education.resume = resume
    >>> education.level = level
    >>> education.school = party
    >>> education.save()

Try replace active party::

    >>> replace = Wizard('party.replace', models=[party])
    >>> replace.form.source = party
    >>> replace.form.destination = party2
    >>> replace.execute('replace')

Check fields have been replaced::

    >>> candidate.reload()
    >>> candidate.party == party2
    True
    >>> resume.reload()
    >>> resume.party == party2
    True
    >>> education.reload()
    >>> education.school == party2
    True
