from Monitor.core.monitor import Monitor, Context  
from Banque.core.metier_banque import ExtractionMetier as application
# from Monitor.core.chrome_Playwright import ChromeDriver
from Monitor.core.chrome_Selenium import ChromeDriver

from Banque.gui.guiBanque import gui
from Monitor.gui.presentation_horizontale import Presentation
from LBP.Excel_LBP import Excel_LBP as Destination

# from LBP.HTML_LBP import HTML_LBP as Source
from LBP.CSV_LBP import CSV_LBP as Source

context=Context()            

context.set_application(appli=application)
context.set_gui(gui=gui)
context.set_presentation(pres=Presentation, pos_gui='gauche', pos_appli='droite')

context.set_appli_param(key='Source', value=Source)
context.set_appli_param(key='Destination', value=Destination)
context.set_appli_param(key='Driver', value=ChromeDriver)
context.set_appli_param(key='tout_traiter', value=False)

app = Monitor(context) 
app.run()          # Application
