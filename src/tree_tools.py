import sys
import math
import ROOT
from array import array
from ROOT import TFile, TTree
import numpy as np
from podio import root_io
import edm4hep



def PDG_ID_to_bool(number: int) -> dict:
    """Maps the PDG ID to the particle type for jets using https://pdg.lbl.gov/2007/reviews/montecarlorpp.pdf """
    particle_map = {
        1: {"recojet_isU": True, "recojet_isD": False, "recojet_isS": False, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": False},
        2: {"recojet_isU": False, "recojet_isD": True, "recojet_isS": False, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": False},
        3: {"recojet_isU": False, "recojet_isD": False, "recojet_isS": True, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": False},
        4: {"recojet_isU": False, "recojet_isD": False, "recojet_isS": False, "recojet_isC": True, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": False},
        5: {"recojet_isU": False, "recojet_isD": False, "recojet_isS": False, "recojet_isC": False, "recojet_isB": True, "recojet_isTAU": False, "recojet_isG": False},
        15: {"recojet_isU": False, "recojet_isD": False, "recojet_isS": False, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": True, "recojet_isG": False},
        21: {"recojet_isU": False, "recojet_isD": False, "recojet_isS": False, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": True},
    }
    return particle_map.get(number, {"recojet_isU": False, "recojet_isD": False, "recojet_isS": False, "recojet_isC": False, "recojet_isB": False, "recojet_isTAU": False, "recojet_isG": False})

def PDG_ID_to_bool_particles(number: int, ntracks: int) -> dict:
    """Maps the PDG ID to the particle type for particles in jet"""
    particle_map = {
        11: {"pfcand_isEl": True, "pfcand_isMu": False, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False},
        -11: {"pfcand_isEl": True, "pfcand_isMu": False, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False},
        13: {"pfcand_isEl": False, "pfcand_isMu": True, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False},
        -13: {"pfcand_isEl": False, "pfcand_isMu": True, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False},
        22: {"pfcand_isEl": False, "pfcand_isMu": False, "pfcand_isGamma": True, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False},
    } 
    # Mappings for charged and neutral hadrons
    if number not in [-11, 11, -13, 13, 22]:
        if ntracks == 0:
            return {"pfcand_isEl": False, "pfcand_isMu": False, "pfcand_isGamma": False, "pfcand_isNeutralHad": True, "pfcand_isChargedHad": False}
        else:
            return {"pfcand_isEl": False, "pfcand_isMu": False, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": True}
    # mapping for leptons and photon
    return particle_map.get(number, {"pfcand_isEl": False, "pfcand_isMu": False, "pfcand_isGamma": False, "pfcand_isNeutralHad": False, "pfcand_isChargedHad": False})

       
        
def initialize(t):
    event_number = array("i", [0])
    n_hit = array("i", [0])
    n_part = array("i", [0])

    hit_chis = ROOT.std.vector("float")()
    hit_x = ROOT.std.vector("float")()
    hit_y = ROOT.std.vector("float")()
    hit_z = ROOT.std.vector("float")()
    hit_px = ROOT.std.vector("float")()
    hit_py = ROOT.std.vector("float")()
    hit_pz = ROOT.std.vector("float")()

    t.Branch("event_number", event_number, "event_number/I")
    t.Branch("n_hit", n_hit, "n_hit/I")
    t.Branch("n_part", n_part, "n_part/I")

    t.Branch("hit_chis", hit_chis)
    t.Branch("hit_x", hit_x)
    t.Branch("hit_y", hit_y)
    t.Branch("hit_z", hit_z)
    t.Branch("hit_px", hit_px)
    t.Branch("hit_py", hit_py)
    t.Branch("hit_pz", hit_pz)
    
    # Parameters from fast sim to be reproduced in full sim
    
    # Jet parameters
    jet_p = array("f", [0])
    t.Branch("jet_p", jet_p, "jet_p/F")
    jet_E = array("f", [0])
    t.Branch("jet_E", jet_E, "jet_E/F")
    jet_mass = array("f", [0])
    t.Branch("jet_mass", jet_mass, "jet_mass/F")
    jet_nconst = array("i", [0])
    t.Branch("jet_nconst", jet_nconst, "jet_nconst/I")
    jet_theta = array("f", [0])
    t.Branch("jet_theta", jet_theta, "jet_theta/F")
    jet_phi = array("f", [0])
    t.Branch("jet_phi", jet_phi, "jet_phi/F")
    # MC truth jet IDs
    recojet_isG = array("B", [0])
    t.Branch("recojet_isG", recojet_isG, "recojet_isG/B")
    recojet_isU = array("B", [0])
    t.Branch("recojet_isU", recojet_isU, "recojet_isU/B")
    recojet_isD = array("B", [0])
    t.Branch("recojet_isD", recojet_isD, "recojet_isD/B")
    recojet_isS = array("B", [0])
    t.Branch("recojet_isS", recojet_isS, "recojet_isS/B")
    recojet_isC = array("B", [0])
    t.Branch("recojet_isC", recojet_isC, "recojet_isC/B")
    recojet_isB = array("B", [0])
    t.Branch("recojet_isB", recojet_isB, "recojet_isB/B")
    recojet_isTAU = array("B", [0])
    t.Branch("recojet_isTAU", recojet_isTAU, "recojet_isTAU/B")
    # particles in jet
    pfcand_e = ROOT.std.vector("float")()
    t.Branch("pfcand_e", pfcand_e)
    pfcand_p = ROOT.std.vector("float")()
    t.Branch("pfcand_p", pfcand_p)
    pfcand_theta = ROOT.std.vector("float")()
    t.Branch("pfcand_theta", pfcand_theta)
    pfcand_phi = ROOT.std.vector("float")()
    t.Branch("pfcand_phi", pfcand_phi)
    pfcand_type = ROOT.std.vector("int")()
    t.Branch("pfcand_type", pfcand_type)
    pfcand_charge = ROOT.std.vector("float")()
    t.Branch("pfcand_charge", pfcand_charge)
    pfcand_isEl = ROOT.std.vector("bool")()
    t.Branch("pfcand_isEl", pfcand_isEl)
    pfcand_isMu = ROOT.std.vector("bool")()
    t.Branch("pfcand_isMu", pfcand_isMu)
    pfcand_isGamma = ROOT.std.vector("bool")()
    t.Branch("pfcand_isGamma", pfcand_isGamma)
    pfcand_isNeutralHad = ROOT.std.vector("bool")()
    t.Branch("pfcand_isNeutralHad", pfcand_isNeutralHad)
    pfcand_isChargedHad = ROOT.std.vector("bool")()
    t.Branch("pfcand_isChargedHad", pfcand_isChargedHad)
    #count number of particles in jet
    jet_nmu = array("i", [0])
    t.Branch("jet_nmu", jet_nmu, "jet_nmu/I")
    jet_nel = array("i", [0])
    t.Branch("jet_nel", jet_nel, "jet_nel/I")
    jet_ngamma = array("i", [0])
    t.Branch("jet_ngamma", jet_ngamma, "jet_ngamma/I")
    jet_nnhad = array("i", [0])
    t.Branch("jet_nnhad", jet_nnhad, "jet_nnhad/I")
    jet_nchad = array("i", [0])
    t.Branch("jet_nchad", jet_nchad, "jet_nchad/I")
    pfcand_erel_log = ROOT.std.vector("float")()
    t.Branch("pfcand_erel_log", pfcand_erel_log)
    pfcand_phirel = ROOT.std.vector("float")()
    t.Branch("pfcand_phirel", pfcand_phirel)
    pfcand_thetarel = ROOT.std.vector("float")()
    t.Branch("pfcand_thetarel", pfcand_thetarel)
    # Covariance parameters of helix!
    pfcand_dptdpt = ROOT.std.vector("float")()
    t.Branch("pfcand_dptdpt", pfcand_dptdpt)
    pfcand_detadeta = ROOT.std.vector("float")()
    t.Branch("pfcand_detadeta", pfcand_detadeta)
    pfcand_dphidphi = ROOT.std.vector("float")()
    t.Branch("pfcand_dphidphi", pfcand_dphidphi)
    pfcand_dxydxy = ROOT.std.vector("float")()
    t.Branch("pfcand_dxydxy", pfcand_dxydxy)
    pfcand_dzdz = ROOT.std.vector("float")()
    t.Branch("pfcand_dzdz", pfcand_dzdz)
    pfcand_dxydz = ROOT.std.vector("float")()
    t.Branch("pfcand_dxydz", pfcand_dxydz)
    pfcand_dphidxy = ROOT.std.vector("float")()
    t.Branch("pfcand_dphidxy", pfcand_dphidxy)
    pfcand_dlambdadz = ROOT.std.vector("float")()
    t.Branch("pfcand_dlambdadz", pfcand_dlambdadz)
    pfcand_dxyc = ROOT.std.vector("float")()
    t.Branch("pfcand_dxyc", pfcand_dxyc)
    pfcand_dxyctgtheta = ROOT.std.vector("float")()
    t.Branch("pfcand_dxyctgtheta", pfcand_dxyctgtheta)
    pfcand_phic = ROOT.std.vector("float")()
    t.Branch("pfcand_phic", pfcand_phic) 
    pfcand_phidz = ROOT.std.vector("float")()
    t.Branch("pfcand_phidz", pfcand_phidz)   
    pfcand_phictgtheta = ROOT.std.vector("float")()
    t.Branch("pfcand_phictgtheta", pfcand_phictgtheta)  
    pfcand_cdz = ROOT.std.vector("float")()
    t.Branch("pfcand_cdz", pfcand_cdz) 
    pfcand_cctgtheta = ROOT.std.vector("float")()
    t.Branch("pfcand_cctgtheta", pfcand_cctgtheta) 
    # discplacement paramters of the track  
    pfcand_dxy = ROOT.std.vector("float")()
    t.Branch("pfcand_dxy", pfcand_dxy)
    pfcand_dz = ROOT.std.vector("float")()
    t.Branch("pfcand_dz", pfcand_dz)
    pfcand_btagSip2dVal = ROOT.std.vector("float")()
    t.Branch("pfcand_btagSip2dVal", pfcand_btagSip2dVal)
    pfcand_btagSip2dSig = ROOT.std.vector("float")()
    t.Branch("pfcand_btagSip2dSig", pfcand_btagSip2dSig)
    pfcand_btagSip3dVal = ROOT.std.vector("float")()
    t.Branch("pfcand_btagSip3dVal", pfcand_btagSip3dVal)
    pfcand_btagSip3dSig = ROOT.std.vector("float")()
    t.Branch("pfcand_btagSip3dSig", pfcand_btagSip3dSig)
    pfcand_btagJetDistVal = ROOT.std.vector("float")()
    t.Branch("pfcand_btagJetDistVal", pfcand_btagJetDistVal)
    pfcand_btagJetDistSig = ROOT.std.vector("float")()
    t.Branch("pfcand_btagJetDistSig", pfcand_btagJetDistSig)
   
    
    

    dic = {
        "hit_chis": hit_chis,
        "hit_x": hit_x,
        "hit_y": hit_y,
        "hit_z": hit_z,
        "hit_px": hit_px,
        "hit_py": hit_py,
        "hit_pz": hit_pz,
        "jet_p": jet_p,
        "jet_E": jet_E,
        "jet_mass": jet_mass,
        "jet_nconst": jet_nconst,
        "jet_theta": jet_theta,
        "jet_phi": jet_phi,
        "recojet_isG": recojet_isG,
        "recojet_isU": recojet_isU,
        "recojet_isD": recojet_isD,
        "recojet_isS": recojet_isS,
        "recojet_isC": recojet_isC,
        "recojet_isB": recojet_isB,
        "recojet_isTAU": recojet_isTAU,
        "pfcand_e": pfcand_e,
        "pfcand_p": pfcand_p,
        "pfcand_theta": pfcand_theta,
        "pfcand_phi": pfcand_phi,
        "pfcand_type": pfcand_type,
        "pfcand_charge": pfcand_charge,
        "pfcand_isEl": pfcand_isEl,
        "pfcand_isMu": pfcand_isMu,
        "pfcand_isGamma": pfcand_isGamma,
        "pfcand_isNeutralHad": pfcand_isNeutralHad,
        "pfcand_isChargedHad": pfcand_isChargedHad,
        "jet_nmu": jet_nmu,
        "jet_nel": jet_nel,
        "jet_ngamma": jet_ngamma,
        "jet_nnhad": jet_nnhad,
        "jet_nchad": jet_nchad,
        "pfcand_erel_log": pfcand_erel_log,
        "pfcand_phirel": pfcand_phirel,
        "pfcand_thetarel": pfcand_thetarel,
        "pfcand_dptdpt": pfcand_dptdpt,
        "pfcand_detadeta": pfcand_detadeta,
        "pfcand_dphidphi": pfcand_dphidphi,
        "pfcand_dxydxy": pfcand_dxydxy,
        "pfcand_dzdz": pfcand_dzdz,
        "pfcand_dxydz": pfcand_dxydz,
        "pfcand_dphidxy": pfcand_dphidxy,
        "pfcand_dlambdadz": pfcand_dlambdadz,
        "pfcand_dxyc": pfcand_dxyc,
        "pfcand_dxyctgtheta": pfcand_dxyctgtheta,
        "pfcand_phic": pfcand_phic,
        "pfcand_phidz": pfcand_phidz,
        "pfcand_phictgtheta": pfcand_phictgtheta,
        "pfcand_cdz": pfcand_cdz,
        "pfcand_cctgtheta": pfcand_cctgtheta,
        "pfcand_dxy": pfcand_dxy,
        "pfcand_dz": pfcand_dz,
        "pfcand_btagSip2dVal": pfcand_btagSip2dVal,
        "pfcand_btagSip2dSig": pfcand_btagSip2dSig,
        "pfcand_btagSip3dVal": pfcand_btagSip3dVal,
        "pfcand_btagSip3dSig": pfcand_btagSip3dSig,
        "pfcand_btagJetDistVal": pfcand_btagJetDistVal,
        "pfcand_btagJetDistSig": pfcand_btagJetDistSig
        
    }
    return (event_number, n_hit, n_part, dic, t)

def clear_dic(dic):
    scalars = ["jet_p", "jet_E", "jet_mass", "jet_nconst", "jet_theta", "jet_phi", \
        "recojet_isG", "recojet_isU", "recojet_isD", "recojet_isS", "recojet_isC", "recojet_isB", "recojet_isTAU", \
        "jet_nmu", "jet_nel", "jet_ngamma", "jet_nnhad", "jet_nchad"]
    for key in dic:
        if key in scalars:
            dic[key][0] = 0
        else:
            dic[key].clear()
    return dic


def store_jet(event, debug, dic, event_number, t):
    """The jets have the following args that can be accessed with dir(jets)
    ['__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__',
    '__dict__', '__dir__', '__dispatch__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
    '__gt__', '__hash__', '__init__', '__init_subclass__', '__invert__', '__le__', '__lt__', '__module__',
    '__mul__', '__ne__', '__neg__', '__new__', '__pos__', '__python_owns__', '__radd__', '__reduce__',
    '__reduce_ex__', '__repr__', '__rmul__', '__rsub__', '__rtruediv__', '__setattr__', '__sizeof__',
    '__smartptr__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__weakref__',
    'addToClusters', 'addToParticleIDs', 'addToParticles', 'addToTracks', 'clone', 'clusters_begin',
    'clusters_end', 'clusters_size', 'covMatrix', 'getCharge', 'getClusters', 'getCovMatrix', 'getEnergy',
    'getGoodnessOfPID', 'getMass', 'getMomentum', 'getObjectID', 'getParticleIDUsed', 'getParticleIDs',
    'getParticles', 'getReferencePoint', 'getStartVertex', 'getTracks', 'getType', 'id', 'isAvailable'
    , 'isCompound', 'momentum', 'operator ReconstructedParticle', 'particleIDs_begin', 'particleIDs_end'
    , 'particleIDs_size', 'particles_begin', 'particles_end', 'particles_size', 'referencePoint',
    'setCharge', 'setCovMatrix', 'setEnergy', 'setGoodnessOfPID', 'setMass', 'setMomentum',
    'setParticleIDUsed', 'setReferencePoint', 'setStartVertex', 'setType', 'tracks_begin',
    'tracks_end', 'tracks_size', 'unlink']

    Args:
        event (_type_): single event from the input rootfile
        debug (_type_): debug flat
        dic (_type_): dic with tree information for output root file

    Returns:
        _type_: _description_
    """

    RefinedVertexJets = "RefinedVertexJets"

    if debug:
        print("")
    for j, jet in enumerate(event.get(RefinedVertexJets)): # loop over the two jets
        clear_dic(dic) # clear the dictionary for new jet

        # Use dir(jet) to print all available bindings
        # print(dir(jet))

        # break
        # Extract the jet momentum
        jet_momentum = jet.getMomentum()
        #print(jet_momentum.x, jet_momentum.y)
        particles_jet = jet.getParticles()
        #print(dir(particles_jet)) # print all available bindings for particles_jet
        """['__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__', '__dict__', '__dir__', '__dispatch__', 
        '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', 
        '__init_subclass__', '__invert__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__mul__', '__ne__', '__neg__', 
        '__new__', '__pos__', '__python_owns__', '__radd__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__rsub__', 
        '__rtruediv__', '__setattr__', '__sizeof__', '__smartptr__', '__str__', '__sub__', '__subclasshook__', '__truediv__', 
        '__weakref__', 'at', 'begin', 'empty', 'end', 'size']
        """
        
        
        #print(jet.getCovMatrix()) # Covariance matrix but only filled with zeros 
        
        
        # calculate angles
        jet_theta = np.arcsin(np.sqrt(jet_momentum.x**2 + jet_momentum.y**2)/np.sqrt(jet_momentum.x**2 + jet_momentum.y**2 + jet_momentum.z**2))
        jet_phi = np.arccos(jet_momentum.x/np.sqrt(jet_momentum.x**2 + jet_momentum.y**2))
        
        # Fill branches of the tree
        dic["jet_p"][0] = np.sqrt(jet_momentum.x**2 + jet_momentum.y**2 + jet_momentum.z**2)
        dic["jet_E"][0] = jet.getEnergy()
        dic["jet_mass"][0] = jet.getMass()
        dic["jet_nconst"][0] = particles_jet.size()
        dic["jet_theta"][0] = jet_theta
        dic["jet_phi"][0] = jet_phi
        # MC truth jet particle IDs
        MC_type = PDG_ID_to_bool(jet.getType()) # returns a dictionary with the particle type
        for key in MC_type:
            dic[key][0] = MC_type[key]
            
        for i, part in enumerate(particles_jet):
            particle = particles_jet.at(i)
            #print(dir(particle)) # print all available bindings for particle
            """
            ['__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__', '__dict__', '__dir__', '__dispatch__', 
            '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', 
            '__invert__', '__le__', '__lt__', '__module__', '__mul__', '__ne__', '__neg__', '__new__', '__pos__', '__python_owns__', 
            '__radd__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__rsub__', '__rtruediv__', '__setattr__', '__sizeof__', 
            '__smartptr__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__weakref__', 'clone', 'clusters_begin', 
            'clusters_end', 'clusters_size', 'getCharge', 'getClusters', 'getCovMatrix', 'getEnergy', 'getGoodnessOfPID', 
            'getMass', 'getMomentum', 'getObjectID', 'getParticleIDUsed', 'getParticleIDs', 'getParticles', 'getReferencePoint', 
            'getStartVertex', 'getTracks', 'getType', 'id', 'isAvailable', 'isCompound', 'makeEmpty', 'particleIDs_begin', 
            'particleIDs_end', 'particleIDs_size', 'particles_begin', 'particles_end', 'particles_size', 'tracks_begin', 'tracks_end', 
            'tracks_size', 'unlink']
            """
            particle_momentum = particle.getMomentum()
            dic["pfcand_e"].push_back(particle.getEnergy())
            dic["pfcand_p"].push_back(np.sqrt(particle_momentum.x**2 + particle_momentum.y**2 + particle_momentum.z**2))
            dic["pfcand_theta"].push_back(np.arcsin(np.sqrt(particle_momentum.x**2 + particle_momentum.y**2)/np.sqrt(particle_momentum.x**2 + particle_momentum.y**2 + particle_momentum.z**2)))
            dic["pfcand_phi"].push_back(np.arccos(particle_momentum.x/np.sqrt(particle_momentum.x**2 + particle_momentum.y**2)))
            dic["pfcand_type"].push_back(particle.getType())
            dic["pfcand_charge"].push_back(particle.getCharge()) 
            MC_particle_type = PDG_ID_to_bool_particles(particle.getType(), particle.getTracks().size()) # dictionary with the particle type (bool)
            for key in MC_particle_type:
                dic[key].push_back(MC_particle_type[key])
            # calculate relative values
            dic["pfcand_erel_log"].push_back(np.log(dic["pfcand_e"][-1]/dic["jet_E"][0]))
            dic["pfcand_phirel"].push_back(dic["pfcand_phi"][-1] - dic["jet_phi"][0]) # same as in  rv::RVec<FCCAnalysesJetConstituentsData> get_phirel_cluster in https://github.com/HEP-FCC/FCCAnalyses/blob/d39a711a703244ee2902f5d2191ad1e2367363ac/analyzers/dataframe/src/JetConstituentsUtils.cc#L2 
            dic["pfcand_thetarel"].push_back(dic["pfcand_theta"][-1] - dic["jet_theta"][0]) 
            
            # get tracks of each particle (should be only one track)
            tracks = particle.getTracks()
            #print(dir(tracks))
            """
            ['__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__', '__dict__', '__dir__', 
            '__dispatch__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', 
            '__init_subclass__', '__invert__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__mul__', '__ne__', '__neg__', '__new__', 
            '__pos__', '__python_owns__', '__radd__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__rsub__', '__rtruediv__', '__setattr__', 
            '__sizeof__', '__smartptr__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__weakref__', 'at', 'begin', 'empty', 'end', 'size']
            """
            #print(dir(tracks.at(0)))
            """
            ['__add__', '__assign__', '__bool__', '__class__', '__delattr__', '__destruct__', '__dict__', '__dir__', '__dispatch__', '__doc__', '__eq__', 
            '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__invert__', '__le__', '__lt__', 
            '__module__', '__mul__', '__ne__', '__neg__', '__new__', '__pos__', '__python_owns__', '__radd__', '__reduce__', '__reduce_ex__', 
            '__repr__', '__rmul__', '__rsub__', '__rtruediv__', '__setattr__', '__sizeof__', '__smartptr__', '__str__', '__sub__', 
            '__subclasshook__', '__truediv__', '__weakref__', 'clone', 'dxQuantities_begin', 'dxQuantities_end', 'dxQuantities_size', 
            'getChi2', 'getDEdx', 'getDEdxError', 'getDxQuantities', 'getNdf', 'getObjectID', 'getRadiusOfInnermostHit', 'getSubdetectorHitNumbers', 
            'getTrackStates', 'getTrackerHits', 'getTracks', 'getType', 'id', 'isAvailable', 'makeEmpty', 'subdetectorHitNumbers_begin', 
            'subdetectorHitNumbers_end', 'subdetectorHitNumbers_size', 'trackStates_begin', 'trackStates_end', 'trackStates_size', 'trackerHits_begin', 
            'trackerHits_end', 'trackerHits_size', 'tracks_begin', 'tracks_end', 'tracks_size', 'unlink']
            """
            if tracks.size() == 1: # charged particle
                track = tracks.at(0)
                #print(track.getRadiusOfInnermostHit())
                #print(particle.getCovMatrix()) # all zero
            elif tracks.size() == 0: # neutral particle -> no track -> set them to zero! DOUBLE CHECK!!!
                dic["pfcand_dptdpt"].push_back(0)
                dic["pfcand_detadeta"].push_back(0)
                dic["pfcand_dphidphi"].push_back(0)
                dic["pfcand_dxydxy"].push_back(0)
                dic["pfcand_dzdz"].push_back(0)
                dic["pfcand_dxydz"].push_back(0)
                dic["pfcand_dphidxy"].push_back(0)
                dic["pfcand_dlambdadz"].push_back(0)
                dic["pfcand_dxyc"].push_back(0)
                dic["pfcand_dxyctgtheta"].push_back(0)
                dic["pfcand_phic"].push_back(0)
                dic["pfcand_phidz"].push_back(0)
                dic["pfcand_phictgtheta"].push_back(0)
                dic["pfcand_cdz"].push_back(0)
                dic["pfcand_cctgtheta"].push_back(0)
                dic["pfcand_dxy"].push_back(0)
                dic["pfcand_dz"].push_back(0)
                dic["pfcand_btagSip2dVal"].push_back(0)
                dic["pfcand_btagSip2dSig"].push_back(0)
                dic["pfcand_btagSip3dVal"].push_back(0)
                dic["pfcand_btagSip3dSig"].push_back(0)
                dic["pfcand_btagJetDistVal"].push_back(0)
                dic["pfcand_btagJetDistSig"].push_back(0)
            else:
                raise ValueError("Particle has more than one track")
        # this needs to be updates to fill the tree with the info as in the fastsim rootfile
        t.Fill()
        # because we want to go from an event based tree to a jet based tree for each jet we add an event
        event_number[0] += 1

    return dic, event_number, t
