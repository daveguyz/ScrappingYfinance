package SeleniumQuick.new2025;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import io.github.bonigarcia.wdm.WebDriverManager;

import java.util.List;

public class App {
    public static void main(String[] args) {
        // Setup ChromeDriver
        WebDriverManager.chromedriver().setup();

        // Enable headless mode
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new"); // new headless mode (faster)
        options.addArguments("--disable-gpu"); // optional, for some OS
        options.addArguments("--window-size=1920,1080"); // avoids some element visibility issues

        WebDriver driver = new ChromeDriver(options);

        try {
            // Visit the SPX options page
            driver.get("https://finance.yahoo.com/quote/%5ESPX/options/");

            // Optional: use WebDriverWait instead of Thread.sleep for speed
            Thread.sleep(3000); // small sleep for dynamic content (can be replaced with WebDriverWait)

            // Locate the table
            WebElement table = driver.findElement(By.cssSelector("table.yf-1oeiges"));

            // Fetch all rows
            List<WebElement> rows = table.findElements(By.tagName("tr"));

            // Iterate and print cells
            for (WebElement row : rows) {
                List<WebElement> cells = row.findElements(By.tagName("td"));
                for (WebElement cell : cells) {
                    System.out.print(cell.getText() + "\t");
                }
                System.out.println();
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            driver.quit();
        }
    }
}
