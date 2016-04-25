#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cPickle
import numpy as np
from scipy.stats import norm
from fastdtw import fastdtw
from time import time
import descritores as desc
from pdist_mt import pdist_mt,set_param

if __name__ == '__main__':
 nc = 32
 raio = np.array([0.05,0.15,0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5,2.75,3.0,3.5])
 # Parâmetros da distância
 kk = 16
 beta = 1.13
 radius = 5
 #sigma = 1.2

 def smooth(x,s):
  N = len(x)
  return np.convolve(np.hstack((x,x,x)),norm(N/2,s).pdf(np.arange(N)),'same')[N:2*N]

  
 def dist(X,Y):
  CX = np.std(X,axis = 1)
  CY = np.std(Y,axis = 1)
  M = len(raio)
  c = 0
  for i in np.arange(M): 
   c = c + fastdtw(X[i],Y[i],radius = radius)[0]/(CX[i] + CY[i] + beta)
  return c

 def pdist(X):
  N = len(X)
  p = np.zeros((N,N))
  for i in np.arange(N):
   for j in np.arange(i,N):
    if i != j:
     p[i,j] = dist(X[i],X[j])
  return p+p.T
   
 db = cPickle.load(open(sys.argv[1]+"classes.txt"))
 names = [i for i in db.keys()]
 cl = db.values()
 N = len(cl)
 # Total de classes
 Nclasses = max(cl)
 # Número de recuperações para base balanceada
 Nretr = N/Nclasses
 print "Calculando descritores"
 tt = time()
 Fl = [np.array([desc.dii(sys.argv[1] + k,raio = r,nc = nc,method = "octave") for r in raio]) for k in names]
 print time() - tt
 Fl_m = [k.mean(axis = 0) for k in Fl]
 #rem = nc%kk
 #limits_lo = np.arange(0,nc,kk)
 #limits_hi= np.arange(kk,nc,kk)
 #idx =[range(lo,hi) for lo,hi in zip(limits_lo[0:len(limits_lo)-1],limits_hi)]
 #if rem:
 # idx = idx + [range(nc-rem,nc)+range(0,kk-rem)]
 #print limits_lo,limits_hi,idx
 Fl_sliced = []
 for vt in Fl_m:
  start = np.abs(vt).argmax()
  rem = nc%kk
  vaux = np.hstack((vt,vt,vt[0:kk+rem]))
  limits_lo = np.arange(start,nc+start,kk)
  limits_hi= np.arange(kk+start,kk+nc+start+rem,kk)
  idx =[range(lo,hi) for lo,hi in zip(limits_lo,limits_hi)]
  Fl_sliced.append(np.array([vaux[i] for i in idx]))
 #F = F/np.tile(np.abs(F).max(axis = 0),(Nc,1))
 #C1.append(F.std(axis = 0).mean())
 #Fl1.append(F.T)
 print "Calculando matriz de distancias"

 #tt = time()
 #md = pdist(Fl)
 #print time() - tt

 set_param(b = beta, r = radius)
 tt = time()
 md = pdist_mt(Fl_sliced,2)
 print time() - tt
 
 l = np.zeros((Nclasses,Nretr),dtype = int)

 for i,nome in zip(np.arange(N),names):
# Para cada linha de md estabelece rank de recuperacao
# O primeiro elemento de cada linha corresponde a forma modelo
# Obtem a classe dos objetos recuperados pelo ordem crescente de distancia
  idx = np.argsort(md[i])
 # pega classes a qual pertencem o primeiro padrao e as imagens recuperadas
  classe_padrao = db[nome]
  name_retr = np.array(names)[idx] 
  aux = np.array([db[j] for j in name_retr])
  classe_retrs = aux[0:Nretr]
  n = np.nonzero(classe_retrs == classe_padrao)
  for i in n[0]:
   l[classe_padrao-1,i] = l[classe_padrao-1,i] + 1 

 v = np.array([l[:,i].sum() for i in np.arange(Nretr)])

 print l
 print v
 print (np.abs(v - 99.)).sum()/v.shape[0]

