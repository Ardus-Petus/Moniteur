# main_CESU.py
from Monitor.core.monitor import Monitor, Context  
from Cesu.metier_CESU import ExtractionMetier as application
from Monitor.gui.guiStandard import gui, gui_update
from Monitor.gui.presentation_horizontale import Presentation

context=Context()            

context.set_application(application)
context.set_gui(gui, gui_update)
context.set_presentation(Presentation, 'gauche', 'droite')

context.set_appli_param('traitement', 'prelevements')

app = Monitor(context) 
app.run()          # Application
