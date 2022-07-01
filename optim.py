import pyomo.environ as pyo
import pyomo.opt as po
from pyomo.opt import SolverFactory
import pandas as pd
from pyomo.environ import *

#pip install pyomo
#pip install cplex
#pip install docplex

def opt(c1,c2,c3,c4,c5,c6,c7,s1,s2,s3,s4,s5,s6,c8,c9):
    #data
    comps = ['BPL', 'CO2', 'SiO2']

    P_i = pd.DataFrame(index=comps)
    P_i['pBrut'] = [c5/100, c6/100, c7/100]
    P_i['pLF'] = [c2/100, c3/100, c4/100]

    P_s = pd.DataFrame(index=comps)
    P_s['s_min'] = [s1/100, s5/100 , s3/100]
    P_s['s_max'] = [s2/100, s6/100 , s4/100]



    # les contraintes de la demande :
    Dexpo =c8  ;
    DG10 = c9  ;

    # qualites ( expo : 0 // standard : 1)
    qualite = c1 ; 

###########################################
    #P_s = pd.DataFrame(index=comps)
    P_s['e_min'] = [0.5819, 0.0497, 0.039]
    P_s['e_max'] = [0.6883, 0.0738, 0.1188]


    # les contraintes de stockage et de production  : 
    # a l'entrer :
    SLF = 3000 
    Sbrut = 6000 

    # a la sortie  :
    Sexpo = 9000  
    SG10 = 9000   

    # production  :
    Prod = 7000 
    D = 0.92;
    Xmax=0.4 

    #coef de la fonction objectif :

    COFF = pd.DataFrame(index=comps)
    COFF['alfa'] = [-4.18631879, 1.51409761e+01, 3.51707753e+01]
    COFF['beta'] = [3.52825280e+01, 2.02366685e+01, -1.13260031e+02]

    qa = -1.10409869e+04 
    cte = 35309.142133385314 

    #''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    pH2O_S = 0.1 
    pH2O_dos = 17 
    debit_enter = 7200 



    # create a model instance
    model = ConcreteModel()

    # declare decision variables
    model.qE = Var(within=NonNegativeReals ,  bounds=(0, 10000))
    model.qLF = Var(within=NonNegativeReals , bounds=(0, 10000))
    model.qBrut = Var(within=NonNegativeReals , bounds=(0, 10000))

    model.qS = Var(within=NonNegativeReals , bounds=(0, 10000) )
    model.qYcc = Var(within=NonNegativeReals , bounds=(0, 10000))
    model.qSout = Var(within=NonNegativeReals , bounds=(0, 10000))
    model.qDos = Var(within=NonNegativeReals , bounds=(0, 10000))
    model.qG10 = Var(within=NonNegativeReals , bounds=(0, 10000))

    model.qe = Var(comps , domain=NonNegativeReals , bounds=(0, 10000))
    model.qycc = Var(comps , domain=NonNegativeReals, bounds=(0, 10000))


    obj_expr = sum(COFF.loc[p, 'alfa'] * model.qe[p] for p in comps)+sum(COFF.loc[p, 'beta'] * model.qycc[p] for p in comps) + qa*qualite +cte 
    model.CF = Objective(expr = obj_expr, sense=minimize)


    model.constrain1 = ConstraintList()



    model.constrain1.add(model.qe['BPL'] ==(model.qLF *P_i.loc[ 'BPL','pLF'] + model.qBrut* P_i.loc[ 'BPL','pBrut']))
    model.constrain1.add(model.qe['CO2'] ==(model.qLF *P_i.loc[ 'CO2','pLF'] + model.qBrut* P_i.loc[ 'CO2','pBrut']))
    model.constrain1.add(model.qe['SiO2'] ==(model.qLF *P_i.loc[ 'SiO2','pLF'] + model.qBrut* P_i.loc[ 'SiO2','pBrut']))
    model.constrain1.add(model.qE == model.qLF + model.qBrut)

    model.constrain1.add(model.qe['BPL'] <= model.qE )
    model.constrain1.add(model.qe['CO2'] <= model.qE )
    model.constrain1.add(model.qe['SiO2'] <= model.qE )
    model.constrain1.add(sum(model.qe[i] for i in comps ) <= model.qE )


    model.constrain1.add( P_s.loc['BPL','e_min']*model.qE<= model.qe['BPL']) 
    model.constrain1.add(model.qe['BPL']<= P_s.loc['BPL' ,'e_max']*model.qE )
    model.constrain1.add( P_s.loc['CO2','e_min']*model.qE<= model.qe['CO2'] )
    model.constrain1.add( model.qe['CO2']<= P_s.loc['CO2' ,'e_max']*model.qE )
    model.constrain1.add( P_s.loc['SiO2','e_min']*model.qE<= model.qe['SiO2'])
    model.constrain1.add( model.qe['SiO2']<= P_s.loc['SiO2' ,'e_max']*model.qE )

    model.constrain1.add(model.qS == model.qYcc +  model.qSout)
    model.constrain1.add(model.qG10 == model.qSout + model.qDos + model.qYcc*qualite)


    model.constrain1.add(model.qycc['BPL'] <= model.qYcc )
    model.constrain1.add(model.qycc['CO2'] <= model.qYcc )
    model.constrain1.add(model.qycc['SiO2'] <= model.qYcc )
    model.constrain1.add(sum(model.qycc[i] for i in comps ) <= model.qYcc )


    model.constrain1.add( P_s.loc['BPL','s_min']*model.qYcc<= model.qycc['BPL'])
    model.constrain1.add( model.qycc['BPL']<= P_s.loc['BPL' ,'s_max']*model.qYcc )  
    model.constrain1.add( P_s.loc['CO2','s_min']*model.qYcc<= model.qycc['CO2'] )
    model.constrain1.add( model.qycc['CO2']<= P_s.loc['CO2' ,'s_max']*model.qYcc )
    model.constrain1.add( P_s.loc['SiO2','s_min']*model.qYcc<= model.qycc['SiO2'] )
    model.constrain1.add( model.qycc['SiO2']<= P_s.loc['SiO2' ,'s_max']*model.qYcc )

    if qualite == 0:
        model.constrain1.add(model.qYcc <= Sexpo )
        model.constrain1.add(Dexpo<= model.qYcc )
    model.constrain1.add(model.qG10<=SG10)
    model.constrain1.add(model.qS<=Prod)
    model.constrain1.add(model.qS==D*model.qE)
    model.constrain1.add(DG10 <= model.qG10 )
    model.constrain1.add(model.qE<= debit_enter)
    model.constrain1.add(pH2O_S*(model.qSout + qualite*model.qYcc)  +pH2O_dos*model.qDos <= 5.5 *model.qG10 ) 
    model.constrain1.add(model.qLF <= Xmax * model.qE)
    model.constrain1.add(0.29*model.qE<=model.qLF)

    solver = pyo.SolverFactory('cplex_direct')
    solver.solve(model)
 
    #convert numbers

    m1 = float('{:.2f}'.format(model.qLF()))
    m2 = float('{:.2f}'.format(model.qBrut()))
    m3 = float('{:.2f}'.format(model.qE()))
    m4 = float('{:.2f}'.format(model.qG10()))
    m5 = float('{:.2f}'.format(model.qYcc()))
    m6 = float('{:.2f}'.format(model.qS()))
    m7 = float('{:.2f}'.format(model.qDos()))
    m8 = float('{:.2f}'.format(model.qSout()))
    m9 = float('{:.2f}'.format(model.CF()))
    resBPL = model.qycc['BPL']() 
    resCO2 = model.qycc['CO2']() 
    resSiO2 = model.qycc['SiO2']() 
    m10 = float('{:.2f}'.format(float(resBPL)))
    m11 = float('{:.2f}'.format(float(resCO2)))
    m12 = float('{:.2f}'.format(float(resSiO2)))

    return [ m1,m2,m3,m4,m5,m6,m7,m8,m10,m11,m12,m9]

"""
# display solution
print('qE  = ', model.qE())
print('qLF = ', model.qLF())
print('qBrut = ', model.qBrut())
print('qS = ', model.qS())
print('qYcc = ', model.qYcc())
print('qSout = ', model.qSout())

print('qDos = ', model.qDos())

print('qG10 = ', model.qG10())
print('Consommation de fuel (kg) = ', model.CF())
print('BPL sortie = ', model.qe['BPL']())
print('CO2 sortie = ', model.qe['CO2']())
print('Sio2 sortie = ', model.qe['SiO2']())
"""