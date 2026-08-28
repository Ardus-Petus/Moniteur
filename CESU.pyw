# main_CESU.py
import os
from Monitor.core.monitor import Monitor, Context  
from Monitor.gui.presentation_horizontale import Presentation
from Cesu.metier_CESU import ExtractionMetier as application
from Cesu.gui_CESU import gui

context=Context()            

context.set_application(application)
context.set_gui(gui)
context.set_presentation(Presentation, 'gauche', 'droite')

context.set_appli_param('Path_out', os.path.join(os.curdir, 'Cesu', 'Résultats')) # répertoire des fichiers de sortie

context.set_gui_param(key='side', value='left') # orientation des boutons

app = Monitor(context)
app.run()          # Application
