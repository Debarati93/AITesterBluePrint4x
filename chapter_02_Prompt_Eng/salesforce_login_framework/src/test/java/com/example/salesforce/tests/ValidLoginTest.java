package com.example.salesforce.tests;

import com.example.salesforce.pages.LoginPage;
import io.github.bonigarcia.wdm.WebDriverManager;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.SkipException;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

public class ValidLoginTest {
    private WebDriver driver;
    private LoginPage loginPage;

    @BeforeTest
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--window-size=1920,1080");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");

        driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        loginPage = new LoginPage(driver);
    }

    @Test
    public void validLoginScenario() {
        String username = System.getProperty("salesforce.username");
        String password = System.getProperty("salesforce.password");

        if (username == null || username.isBlank() || password == null || password.isBlank()) {
            throw new SkipException("Set -Dsalesforce.username and -Dsalesforce.password to execute the valid login test.");
        }

        try {
            loginPage.open("https://login.salesforce.com/?locale=in");
            loginPage.login(username, password);
            Assert.assertFalse(loginPage.isErrorDisplayed(), "Valid credentials should not show an error message.");
        } catch (RuntimeException e) {
            throw new AssertionError("The valid login scenario failed.", e);
        }
    }

    @AfterTest
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
