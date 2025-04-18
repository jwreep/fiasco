"""
CHIANTI IDL Comparison: Continuum
==================================

Compare the free-free and free-bound calculations to that in the CHIANTI IDL routines.
"""
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np

from astropy.visualization import quantity_support

import fiasco

from fiasco.tests.idl.helpers import read_idl_test_output
from fiasco.util.setup_db import LATEST_VERSION

quantity_support()

################################################
# Define a function for comparing and plotting
# the outputs from fiasco and IDL. Note that we have precomputed
# the IDL outputs.
def plot_idl_comparison(wavelength, temperature, result_fiasco, result_idl):
    wave_mesh, temp_mesh = np.meshgrid(wavelength, temperature)
    temp_mesh = temp_mesh.to_value('K')
    wave_mesh = wave_mesh.to_value('Angstrom')
    result_fiasco = result_fiasco.to_value('erg cm3 s-1 Angstrom-1')
    result_idl = result_idl.to_value('erg cm3 s-1 Angstrom-1')
    difference = result_fiasco - result_idl
    difference_norm = difference / result_idl

    fig = plt.figure(figsize=(10,10))
    axes = fig.subplot_mosaic(
        """
        AABB
        .CC.
        """,
        sharex=True,
        sharey=True,
    )
    norm = matplotlib.colors.LogNorm(vmin=1e-30,vmax=1e-26)
    # IDL result
    im = axes['A'].pcolormesh(temp_mesh, wave_mesh, result_idl, norm=norm)
    axes['A'].set_title('IDL')
    axes['A'].set_xscale('log')
    axes['A'].set_xlabel('Temperature [K]')
    axes['A'].set_ylabel(r'Wavelength [$\AA$]')
    # fiasco result
    im = axes['B'].pcolormesh(temp_mesh, wave_mesh, result_fiasco, norm=norm)
    axes['B'].set_title('fiasco')
    fig.colorbar(im, ax=[axes['A'], axes['B']], orientation='horizontal')
    # Normalized difference
    im = axes['C'].pcolormesh(temp_mesh, wave_mesh, difference_norm,
                              norm=matplotlib.colors.SymLogNorm(1e-3, vmin=-1, vmax=1),
                              cmap='RdBu')
    axes['C'].set_title('Normalized Difference')
    fig.colorbar(im, ax=axes['C'])
    plt.show()


################################################
# First, let's compare the outputs for the free-free
# continuum emission, i.e. that emission produced by
# thermal bremsstrahlung.
idl_result_freefree = read_idl_test_output('freefree_all_ions', LATEST_VERSION)
ion_kwargs = {'abundance': idl_result_freefree['abundance'],
              'ionization_fraction': idl_result_freefree['ionization_fraction']}
all_ions = [fiasco.Ion(ion_name, idl_result_freefree['temperature'], **ion_kwargs) for ion_name in fiasco.list_ions()]
all_ions = fiasco.IonCollection(*all_ions)
free_free = all_ions.free_free(idl_result_freefree['wavelength'])
plot_idl_comparison(idl_result_freefree['wavelength'],
                    idl_result_freefree['temperature'],
                    free_free,
                    idl_result_freefree['free_free'])
print(f'CHIANTI database {idl_result_freefree['database_version']}')
print(f'CHIANTI IDL {idl_result_freefree['chianti_idl_version']}')
print('IDL code to produce free-free result:')
print(idl_result_freefree['idl_script'])

################################################
# Next, let's compare the outputs for the free-bound
# continuum emission.
idl_result_freebound = read_idl_test_output('freebound_all_ions', LATEST_VERSION)
ion_kwargs = {'abundance': idl_result_freebound['abundance'],
              'ionization_fraction': idl_result_freebound['ionization_fraction']}
all_ions = [fiasco.Ion(ion_name, idl_result_freebound['temperature'], **ion_kwargs) for ion_name in fiasco.list_ions()]
all_ions = fiasco.IonCollection(*all_ions)
free_bound = all_ions.free_bound(idl_result_freebound['wavelength'])
plot_idl_comparison(idl_result_freebound['wavelength'],
                    idl_result_freebound['temperature'],
                    free_bound,
                    idl_result_freebound['free_bound'])
print(f'CHIANTI database {idl_result_freebound['database_version']}')
print(f'CHIANTI IDL {idl_result_freebound['chianti_idl_version']}')
print('IDL code to produce free-bound result:')
print(idl_result_freebound['idl_script'])

################################################
# Finally, let's compare the outputs for the two-photon
# continuum emission.
idl_result_twophoton = read_idl_test_output('twophoton_all_ions', LATEST_VERSION)
ion_kwargs = {'abundance': idl_result_twophoton['abundance'],
              'ionization_fraction': idl_result_twophoton['ionization_fraction']}
all_ions = [fiasco.Ion(ion_name, idl_result_twophoton['temperature'], **ion_kwargs) for ion_name in fiasco.list_ions()]
all_ions = fiasco.IonCollection(*all_ions)
two_photon = all_ions.two_photon(idl_result_twophoton['wavelength'], idl_result_twophoton['density']).squeeze()
plot_idl_comparison(idl_result_twophoton['wavelength'],
                    idl_result_twophoton['temperature'],
                    two_photon,
                    idl_result_twophoton['two_photon_continuum'])
print(f'CHIANTI database {idl_result_twophoton['database_version']}')
print(f'CHIANTI IDL {idl_result_twophoton['chianti_idl_version']}')
print('IDL code to produce two-photon result:')
print(idl_result_twophoton['idl_script'])
