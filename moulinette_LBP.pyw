
# main_CESU.py
from Monitor.core.monitor import Monitor, Context  
from LBP.Excel_LBP import Excel_LBP as Excel
from LBP.HTML_LBP import HTML_LBP as HTML
from Banque.core.extraction_metier import ExtractionMetier as application
from Banque.gui.guiBanque import gui, gui_update
from Monitor.gui.presentation_horizontale import Presentation

context=Context()            

context.set_application(application)
context.set_gui(gui, gui_update)
context.set_presentation(Presentation, 'gauche', 'droite')

context.set_appli_param('Excel', Excel)
context.set_appli_param('HTML', HTML)

app = Monitor(context) 
app.run()          # Application
