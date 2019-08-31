"""Version."""

#   (major, minor, micro, release type, pre-release build, post-release build)
version_info = (6, 0, 0, 'final', 0, 0)


def _version():
    """
    Get the version (PEP 440).

    Version structure
      (major, minor, micro, release type, pre-release build, post-release build)
    Release names are named is such a way they are sortable and comparable with ease.
      (alpha | beta | candidate | final)

    - "final" should never have a pre-release build number
    - pre-releases should have a pre-release build number greater than 0
    - post-release is only applied if post-release build is greater than 0
    """

    releases = {"alpha": 'a', "beta": 'b', "candidate": 'rc', "final": ''}
    # Version info should be proper length
    assert len(version_info) == 6
    # Should be a valid release
    assert version_info[3] in releases
    # Pre-release releases should have a pre-release value
    assert version_info[3] == 'final' or version_info[4] > 0
    # Final should not have a pre-release value
    assert version_info[3] != 'final' or version_info[4] == 0

    main = '.'.join(str(x)for x in (version_info[0:2] if version_info[2] == 0 else version_info[0:3]))
    prerel = releases[version_info[3]]
    prerel += str(version_info[4]) if prerel else ''
    postrel = '.post%d' % version_info[5] if version_info[5] > 0 else ''

    return ''.join((main, prerel, postrel))


version = _version()
