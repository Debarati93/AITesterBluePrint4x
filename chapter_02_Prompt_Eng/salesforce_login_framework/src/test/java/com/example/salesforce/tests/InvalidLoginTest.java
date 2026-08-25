package com.example.salesforce.tests;

import com.example.salesforce.pages.LoginPage;
import io.github.bonigarcia.wdm.WebDriverManager;
import java.time.Duration;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

public class InvalidLoginTest {
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
    public void invalidLoginScenario() {
        try {
            loginPage.open("https://login.salesforce.com/?locale=in");
            loginPage.login("invalid.user@example.com", "WrongPassword123!");
            Assert.assertTrue(loginPage.isErrorDisplayed(), "Invalid credentials should display an error message.");
            Assert.assertFalse(loginPage.getErrorMessage().isBlank(), "Error message should not be blank.");
        } catch (RuntimeException e) {
            throw new AssertionError("The invalid login scenario failed.", e);
        }
    }

    @AfterTest
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
