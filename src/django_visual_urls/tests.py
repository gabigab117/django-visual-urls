from django.core.management import call_command


def test_visualize_command_creates_file(tmp_path, monkeypatch):
    """
    Given a temporary directory
    When I run the visualize command
    Then the url_map.html file should be created
    And it should contain Mermaid graph syntax
    And it should contain URL and view style definitions
    And it should include the home view
    And it should include the about view
    And it should include nested URL patterns with sub_view
    And the nested pattern should link to the sub_view
    """
    # Temporarily change working directory so the file is created in tmp_path
    monkeypatch.chdir(tmp_path)
    
    call_command('visualize')
    
    expected_file = tmp_path / "url_map.html"
    assert expected_file.exists(), "The url_map.html file was not created"
    
    content = expected_file.read_text(encoding='utf-8')
    
    # Content verification
    assert "graph LR" in content
    assert "classDef url" in content
    # Module name changes since the file was moved into the package
    assert "view_django_visual_urls_tests_urls_home" in content
    # The 'about/' pattern being a direct view, we should find the view node
    assert "view_django_visual_urls_tests_urls_about" in content
    
    # Test recursivity (include)
    # 1. The 'nested/' folder node
    assert "url__nested_" in content 
    # 2. The view inside 'nested/test/'
    assert "view_django_visual_urls_tests_urls_sub_view" in content
    # 3. The link between parent and child
    assert "url__nested_ --> view_django_visual_urls_tests_urls_sub_view" in content

def test_visualize_command_with_admin(tmp_path, monkeypatch):
    """
    Given a temporary directory
    When I run the visualize command with the --include-admin flag
    Then the url_map.html file should be created
    And it should contain admin URLs
    """
    monkeypatch.chdir(tmp_path)
    
    call_command('visualize', include_admin=True)
    expected_file = tmp_path / "url_map.html"
    assert expected_file.exists()
    
    content = expected_file.read_text(encoding='utf-8')
    assert "admin" in content
