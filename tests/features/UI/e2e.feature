@MCC
@E2E
@UI
@ANY_ENV
Feature: E2E tests for MCC

  @TRID_C2667192
  Scenario: Upload a local file, use all checkers and check Web report
    Given go to the MCC page
    Given a local file "./data/ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc" is uploaded
    Given select "ACDD" checker with version "1.3"
    Given select "CF" checker with version "1.6"
    Given select "GDS2" checker with version "L4"
    Given select "Web Page" as an output format
    When press the upload button
    Then the report is generated for "ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc" granule
    Then the "ACDD" checker version "1.3" is used
    Then the "CF" checker version "1.6" is used
    Then the "GDS2" checker version "L4" is used


  @TRID_C2667193
  @Ignore
  Scenario: Select an url, use all checkers and check PDF report
    Given go to the MCC page
    Given an url "./data/ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc" added for upload
    Given select "ACDD" checker with version "1.1"
    Given select "CF" checker with version "1.7"
    Given select "GDS2" checker with version "L2P"
    Given select "PDF" as an output format
    When press the upload button
    Then a PDF file is generated


  @TRID_C4342789
  Scenario: Upload a 2gb http limit oversized local file, use all checkers and verify error report content
    Given go to the MCC page
    Given create file "./tempdata/oversized.nc" that is equal to "2gb"
    Given a local file "./tempdata/oversized.nc" is uploaded
    Given select "ACDD" checker with version "1.1"
    Given select "CF" checker with version "1.7"
    Given select "GDS2" checker with version "L2P"
    Given select "Web Page" as an output format
    When press the upload button
    Then the error code on the error page is "403 ERROR"
    Then an error page is shown with text "Request blocked."
    Then an error page is shown with text "We can't connect to the server for this app or website at this time. There might be too much traffic or a configuration error. Try again later, or contact the app or website owner."


  @TRID_C4342790
  Scenario: Upload an MCC limit oversized local file, use all checkers and verify error report content
    Given go to the MCC page
    Given get the MCC limit from the MCC page and save it to "MCC limit" parameter
    Given create file "./tempdata/oversized.nc" that is equal to "MCC limit"
    Given a local file "./tempdata/oversized.nc" is uploaded
    Given select "ACDD" checker with version "1.3"
    Given select "CF" checker with version "1.7"
    Given select "GDS2" checker with version "L3"
    Given select "Web Page" as an output format
    When press the upload button
    Then the large file warning shows up on the webpage
    Then the progress bar stops
    Then the main page is still shown after "900" seconds


  @TRID_C4433256
  Scenario: Upload an empty local file, use all checkers and verify error report content
    Given go to the MCC page
    Given create file "./tempdata/empty.nc" that is equal to "100mb"
    Given a local file "./tempdata/empty.nc" is uploaded
    Given select "ACDD" checker with version "1.1"
    Given select "CF" checker with version "1.7"
    Given select "GDS2" checker with version "L4"
    Given select "Web Page" as an output format
    When press the upload button
    Then an unable to read page is shown with title "Unable to read file"
    #Then an unable to read page is shown with text "Your file must be in an accepted data format - .gz, .bz2, .nc, .h5, .nc4 or .hdf"
