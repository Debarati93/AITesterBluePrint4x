package com.example.salesforce.pages;

import java.time.Duration;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginPage {
    private final WebDriver driver;
    private final WebDriverWait wait;

    @FindBy(xpath = "//input[contains(@placeholder,'Username') or contains(@aria-label,'Username') or contains(@type,'email')]")
    private WebElement usernameInput;

    @FindBy(xpath = "//input[contains(@placeholder,'Password') or contains(@aria-label,'Password') or @type='password']")
    private WebElement passwordInput;

    @FindBy(xpath = "//input[contains(@value,'Log In') and @type='submit']")
    private WebElement loginButton;

    @FindBy(xpath = "//input[@type='checkbox' and (contains(@name,'remember') or contains(@id,'remember') or contains(@aria-label,'Remember me'))]")
    private WebElement rememberMeCheckbox;

    @FindBy(xpath = "//div[contains(@class,'error') or contains(@class,'slds-form-element__help') or contains(.,'Please check your username and password') or contains(.,'username and password')]")
    private WebElement loginError;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        PageFactory.initElements(driver, this);
    }

    public void open(String url) {
        try {
            driver.get(url);
            wait.until(ExpectedConditions.urlContains("salesforce.com"));
        } catch (Exception e) {
            throw new RuntimeException("Unable to open Salesforce login page.", e);
        }
    }

    public void login(String username, String password) {
        try {
            wait.until(ExpectedConditions.visibilityOf(usernameInput)).clear();
            usernameInput.sendKeys(username);
            wait.until(ExpectedConditions.visibilityOf(passwordInput)).clear();
            passwordInput.sendKeys(password);
            wait.until(ExpectedConditions.elementToBeClickable(loginButton)).click();
        } catch (TimeoutException | NoSuchElementException e) {
            throw new RuntimeException("Unable to perform login action on Salesforce login page.", e);
        }
    }

    public boolean isErrorDisplayed() {
        try {
            return wait.until(ExpectedConditions.visibilityOf(loginError)).isDisplayed();
        } catch (TimeoutException e) {
            return false;
        }
    }

    public boolean isRememberMeSelected() {
        try {
            return wait.until(ExpectedConditions.visibilityOf(rememberMeCheckbox)).isSelected();
        } catch (TimeoutException | NoSuchElementException e) {
            return false;
        }
    }

    public void setRememberMe(boolean checked) {
        try {
            WebElement element = wait.until(ExpectedConditions.elementToBeClickable(rememberMeCheckbox));
            if (element.isSelected() != checked) {
                element.click();
            }
        } catch (TimeoutException | NoSuchElementException e) {
            throw new RuntimeException("Unable to set remember me option.", e);
        }
    }

    public String getErrorMessage() {
        if (isErrorDisplayed()) {
            return loginError.getText();
        }
        return "";
    }
}
