# main_CESU.py
from Monitor.core.monitor import Monitor, Context  
from Monitor.gui.presentation_horizontale import Presentation
from Cesu.metier_CESU import ExtractionMetier as application
from Cesu.gui_CESU import gui
from Monitor.core.chrome_Playwright import ChromeDriver

context=Context()            

context.set_application(application)
context.set_gui(gui)
context.set_presentation(Presentation, 'gauche', 'droite')
context.set_appli_param(key='Driver', value=ChromeDriver)

app = Monitor(context)
app.run()          # Application
