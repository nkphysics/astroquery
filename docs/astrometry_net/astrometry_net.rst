.. doctest-skip-all

.. _astroquery.astrometry_net:

************************************************************
Astrometry.net plate solutions (`astroquery.astrometry_net`)
************************************************************

Getting started
===============

The module `astroquery.astrometry_net` provides the astroquery interface to
the `astrometry.net`_ plate solving service. Given a list of known sources in
an image and their fluxes or an image, `astrometry.net`_ matches the image to
the sky and constructs a WCS solution.

To use `astroquery.astrometry_net` you will need to set up an account at
`astrometry.net`_ and get your API key. The API key is available under your
profile at `astrometry.net`_ when you are logged in.

Setting API key for astroquery.astrometry_net
---------------------------------------------

Adding API key to astroquery.cfg
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Go to https://nova.astrometry.net and sign in.
2. Copy your API key
3. Add the following to your config file located at ``$HOME/.astropy/config/astroquery.cfg``

.. code-block:: python

    [astrometry_net]

    ## The Astrometry.net API key.
    api_key =

    ## Name of server
    server = http://nova.astrometry.net

    ## Default timeout for connecting to server
    timeout = 120

4. Add your API key to the config file!

For more information about `astropy.config`, see: https://docs.astropy.org/en/stable/config/index.html

Using keyring to store API key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can use the `keyring <https://pypi.org/project/keyring>`_ library to store your API key.

.. code-block:: python

    >>> import keyring
    >>> keyring.set_password('astroquery:astrometry_net', None, 'apikeyhere')

If you have multiple users and keys you can change ``None`` to another name to assign usernames to different keys.

Now you can include the ``keyring`` module to set your API key.

.. code-block:: python

    >>> import keyring
    >>> from astroquery.astrometry_net import AstrometryNet
    WARNING: Astrometry.net API key not found in configuration file [astroquery.astrometry_net.core]
    WARNING: You need to manually edit the configuration file and add it [astroquery.astrometry_net.core]
    WARNING: You may also register it for this session with AstrometryNet.key = 'XXXXXXXX' [astroquery.astrometry_net.core]
    >>> ast = AstrometryNet()
    WARNING: Astrometry.net API key not found in configuration file [astroquery.astrometry_net.core]
    WARNING: You need to manually edit the configuration file and add it [astroquery.astrometry_net.core]
    WARNING: You may also register it for this session with AstrometryNet.key = 'XXXXXXXX' [astroquery.astrometry_net.core]
    >>> ast.api_key = keyring.get_password('astroquery:astrometry_net', '')

For multiple users, replace the empty argument with the desired username.

.. code-block:: python

    >>> ast.api_key = keyring.get_password('astroquery:astrometry_net', 'username')

.. note::

    Be aware that some information you submit to `astrometry.net`_ is publicly
    available even if the raw image isn't. For example, the log of each job
    is accessible if one knows the job id regardless of the permissions set
    for the image. The log will contain the RA/Dec of the solution.

    For publicly viewable images  or source lists `astrometry.net`_ includes
    links to download the FITS files for the image.


Solving from a list of sources
==============================

The most efficient way to use `astrometry.net`_ is to pass it a list of
sources in an image instead of uploading the entire image. The data can  be in
an `astropy.table.Table`, pandas data frame or something other structure.

The only important requirement is that **the list must be sorted by flux in
descending order**.

In the example below, assume that ``catalog.fits`` is a table of pixel positions
(columns ``X_IMAGE`` and ``Y_IMAGE``) and flux (column ``FLUX``) and perhaps
other columns, and that the image is 3073 by 2048 pixels.

The ``solve_timeout`` used below is the time, in seconds, to allow the
`astrometry.net`_ server to find a solution. It typically makes sense for this
to be a longer time than the timeout set in
`astroquery.astrometry_net.AstrometryNetClass.TIMEOUT`, which is intended to
act primarily as a timeout for network transactions.

TODO: Insert link to an actual catalog

.. code-block:: python

    from astropy.table import Table
    from astroquery.astrometry_net import AstrometryNet

    ast = AstrometryNet()
    ast.api_key = 'XXXXXXXXXXXXXXXX'

    sources = Table.read('catalog.fits')
    # Sort sources in ascending order
    sources.sort('FLUX')
    # Reverse to get descending order
    sources.reverse()

    image_width = 3073
    image_height = 2048
    wcs_header = ast.solve_from_source_list(sources['X_IMAGE'], sources['Y_IMAGE'],
                                            image_width, image_height,
                                            solve_timeout=120)

If `astrometry.net`_ is able to find a solution it is returned as an
`astropy.io.fits.Header`. If it is unable to find a solution an empty
dictionary is returned instead. For more details, see
:ref:`handling_results`.

Solving from an image
=====================

The method :meth:`~astroquery.astrometry_net.AstrometryNetClass.solve_from_image`
uploads the entire image file to the `astrometry.net`_ server. The remote service
then detects sources automatically and attempts to compute an astrometric (plate)
solution.

.. important::

    Uploading a full image transfers roughly **10,000 times more data** than
    uploading a pre-detected source list. In nearly all cases it is faster to
    detect sources locally yourself and then call
    :meth:`~astroquery.astrometry_net.AstrometryNetClass.solve_from_source_list`
    instead.

For example:

.. code-block:: python

    from astroquery.astrometry_net import AstrometryNet
    ast = AstrometryNet()
    ast.api_key = 'XXXXXXXXXXXXXXXX'
    wcs_header = ast.solve_from_image('/path/to/image.fit')

.. note::

    As of astroquery 0.4.8+ the previous option to automatically detect sources
    locally using `photutils` (when ``force_image_upload=False``) has been deprecated,
    and as of astroquery 0.4.12+, is entirely removed. The parameters ``fwhm`` and
    ``detect_threshold`` are retained for backwards compatibility only and are
    ignored in the current implementation. If you need to solve from a source list,
    detect sources yourself (e.g. with `photutils` or another package) and use
    :meth:`~astroquery.astrometry_net.AstrometryNetClass.solve_from_source_list`.

If `astrometry.net`_ is able to find a solution it is returned as an
`astropy.io.fits.Header`. If it is unable to find a solution an empty
dictionary is returned instead. For more details, see
:ref:`handling_results`.

.. _handling_results:

Testing for success, failure and time outs
==========================================

There are three outcomes from a call to either
`~astroquery.astrometry_net.AstrometryNetClass.solve_from_source_list` or
`~astroquery.astrometry_net.AstrometryNetClass.solve_from_image`.

+ The solve succeeds: the return value is an
  `astropy.io.fits.Header` generated by `astrometry.net`_ whose content
  is the WCS solution.
+ The solve fails: the return value is an empty dictionary.
+ The solve neither succeeds nor fails before it times out: A
  ``TimeoutError`` is raised. This
  does *not* mean the job has failed. It simply means the solve did not
  complete in the time allowed by the ``solve_timeout`` argument, whose
  default value is
  `astroquery.astrometry_net.AstrometryNetClass.TIMEOUT`. In this case
  it often makes sense to recheck the submission.

Code to handle these cases looks something like this:

.. code-block:: python

    from astroquery.astrometry_net import AstrometryNet

    ast = AstrometryNet()
    ast.api_key = 'XXXXXXXXXXXXXXXX'

    try_again = True
    submission_id = None

    while try_again:
        try:
            if not submission_id:
                wcs_header = ast.solve_from_image('/path/to/image.fit',
                                                  submission_id=submission_id)
            else:
                wcs_header = ast.monitor_submission(submission_id,
                                                    solve_timeout=120)
        except TimeoutError as e:
            submission_id = e.args[1]
        else:
            # got a result, so terminate
            try_again = False

    if wcs_header:
        # Code to execute when solve succeeds
    else:
        # Code to execute when solve fails


.. _common_settings:

Settings common to all solve methods
====================================

In order to speed up the astrometric solution it is possible to pass a
dictionary of  settings to
`~astroquery.astrometry_net.AstrometryNetClass.solve_from_source_list` or
`~astroquery.astrometry_net.AstrometryNetClass.solve_from_image`. If no
settings are passed to the build function then a set of default parameters
will be used, although this will increase the time it takes astrometry.net to
generate a solution. It is recommended to at least set the bounds of the pixel
scale to a reasonable value.

Most of the following descriptions are taken directly from
`astrometry.net`_.

Scale
-----

It is important to set the pixel scale of the image as accurate as possible to increase the
speed of astrometry.net. From astrometry.net: "Most digital-camera images are at least 10
degrees wide; most professional-grade telescopes are narrower than 2 degrees."

Several parameters are available to set the pixel scale.

    ``scale_units``
        - Units used by pixel scale variables
        - Possible values:
            * ``arcsecperpix``: arcseconds per pixel
            * ``arcminwidth``: width of the field (in arcminutes)
            * ``degwidth``:width of the field (in degrees)
            * ``focalmm``: focal length of the lens (for 35mm film equivalent sensor)
    ``scale_type``
        - Type of scale used
        - Possible values:
            * ``ul``: Set upper and lower bounds. If ``scale_type='ul'`` the parameters
              ``scale_upper`` and ``scale_lower`` must be set to the upper and lower bounds
              of the pixel scale respectively
            * ``ev``: Set the estimated value with a given error. If ``scale_type='ev'`` the
              parameters ``scale_est`` and ``scale_err`` must be set to the estiimated value
              (in pix) and error (percentage) of the pixel scale.

Parity
------

Flipping an image reverses its "parity". If you point a digital camera at the sky and
submit the JPEG, it probably has negative parity. If you have a FITS image, it probably
has positive parity. Selecting the right parity will make the solving process run faster,
but if in doubt just try both. ``parity`` can be set to the following values:

    - ``0``: positive parity
    - ``1``: negative parity
    - ``2``: try both

Star Positional Error
---------------------

When we find a matching "landmark", we check to see how many of the stars in your field
match up with stars we know about. To do this, we need to know how much a star in your
field could have moved from where it should be.

The unit for positional error is in pixels and is set by the key ``positional_error``.

Limits
------

In order to narrow down our search, you can supply a field center along with a radius.
We will only search in indexes which fall within this area.

To set limits use all of the following parameters:
    ``center_ra``: center RA of the field (in degrees)
    ``center_dec``: center DEC of the field (in degrees)
    ``radius``: how far the actual RA and DEC might be from the estimated values (in degrees)

Tweak
-----

By default we try to compute a SIP polynomial distortion correction with order 2.
You can disable this by changing the order to 0, or change the polynomial order by setting
``tweak_order``.

CRPIX Center
------------

By default the reference point (CRPIX) of the WCS we compute can be anywhere in your image,
but often it's convenient to force it to be the center of the image. This can be set by choosing
``crpix_center=True``.

License and Sharing
-------------------

The Astrometry.net [website](https://nova.astrometry.net/) allows users to upload images
as well as catalogs to be used in generating an astrometric solution, so the site gives
users the choice of licenses for their publically available images. Since the astroquery
astrometry.net api is only uploading a source catalog the choice of ``public_visibility``,
``allow_commercial_use``, and ``allow_modifications`` are not really relevant and can be left
to their defaults, although their settings are described below

Visibility
^^^^^^^^^^

By default all images/source lists uploaded are publicly available. To change this use the setting
``publicly_visible='n'``.

.. note::

    Be aware that some information you submit to `astrometry.net`_ is publicly
    available even if the raw image isn't. For example, the log of each job
    is accessible if one knows the job id regardless of the permissions set
    for the image. The log will contain the RA/Dec of the solution.

    For publicly viewable images `astrometry.net`_ includes links to download
    the FITS files for the image.

License
^^^^^^^

There are two parameters that describe setting a license:
    ``allow_commercial_use``:
        Chooses whether or not an image uploaded to astrometry.net is licensed
        for commercial use. This can either be set to ``y``, ``n``, or ``d``, which
        uses the default license associated with the api key.
    ``allow_modifications``:
        Whether or not images uploaded to astrometry.net are allowed to be modified by
        other users. This can either be set to ``y``, ``n``, or ``d``, which
        uses the default license associated with the api key.

Debugging Options
^^^^^^^^^^^^^^^^^

To inspect the data being sent to the server for debugging purposes without
making a network call, you can use the following parameter:

``get_query_payload``
    If set to ``True``, returns the prepared query payload and does not send
    the request to the external server. No job is created and no solution is
    returned. This allows verification of parameters, source lists, or image
    headers before submitting an actual solve operation.

Reference/API
=============

.. automodapi:: astroquery.astrometry_net
    :no-inheritance-diagram:

.. _astrometry.net: https://astrometry.net/
.. _photutils: https://photutils.readthedocs.io/en/stable/
