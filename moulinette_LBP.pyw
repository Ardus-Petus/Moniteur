
# main_CESU.py
from Monitor.core.monitor import Monitor  
from LBP.Excel_LBP import Excel_LBP as Excel
from LBP.HTML_LBP import HTML_LBP as HTML
from Banque.core.extraction_metier import ExtractionMetier as application
from Banque.gui.guiBanque import gui, gui_update
from Monitor.gui.presentation_horizontale import Presentation

            
context = {
    'gui':{},
    'appli':{},
    'core':{}
}

context['core']['application'] = application
context['core']['gui'] = (gui, gui_update)
context['core']['presentation'] = (Presentation, 'gauche', 'droite')

context['appli']['Excel'] = Excel
context['appli']['HTML'] = HTML

app = Monitor(context) 
app.run()          # Application
