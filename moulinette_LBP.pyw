

from Monitor.core.monitor import Monitor, Context  
from LBP.Excel_LBP import Excel_LBP as Excel
from LBP.HTML_LBP import HTML_LBP as HTML
from Banque.core.extraction_metier import ExtractionMetier as application
from Banque.gui.guiBanque import gui
from Monitor.gui.presentation_horizontale import Presentation

context=Context()            

context.set_application(appli=application)
context.set_gui(gui=gui)
context.set_presentation(pres=Presentation, pos_gui='gauche', pos_appli='droite')

context.set_appli_param(key='Excel', value=Excel)
context.set_appli_param(key='HTML', value=HTML)

app = Monitor(context) 
app.run()          # Application
