# main_CESU.py
from Monitor.core.monitor import Monitor  
from Cesu.metier_CESU import ExtractionMetier as application
from Monitor.gui.guiStandard import gui, gui_update
from Monitor.gui.presentation_horizontale import Presentation

context = {
    'gui':{},
    'appli':{},
    'core':{}
}

context['core']['application'] = application
context['core']['gui'] = (gui, gui_update)
context['core']['presentation'] = (Presentation,'gauche', 'droite')

context['appli']['traitement'] = 'declarations'
app = Monitor(context) 
app.run()          # Application

