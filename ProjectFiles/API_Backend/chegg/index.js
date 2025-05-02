// Simplified version of the file to test cookie rotation
const { Client, Intents } = require("discord.js");
const moment = require("moment-timezone");
const fs = require("fs");
const client = require('./p.js');

const reviewFilePath = 'review.txt';
const request = require("request");
const axios = require("axios");
const {
  MessageEmbed,
  MessageActionRow,
  MessageButton,
} = require("discord.js");
const crypto = require("crypto");
const adminUserId = "1141758865956937868";
let channelIds = fs
  .readFileSync("channels.txt", "utf8")
  .split("\n")
  .map((line) => line.trim());

// Cloudflare R2 configuration
const AWS = require("aws-sdk");
const s3 = new AWS.S3({
  endpoint: "https://5efcf31036555cada8027860834418a3.r2.cloudflarestorage.com",
  accessKeyId: "4308b65079ed42849ce9172c75618403",
  secretAccessKey: "b89ed19cd69f94c2b8a3d6059350edce382a97201b45bce22387ffc8c4b10b45",
  signatureVersion: "v4",
  region: "auto", // Region is auto for Cloudflare R2
  s3ForcePathStyle: true // Required for Cloudflare R2
});

const R2_BUCKET_NAME = 'homework';
const R2_FOLDER = 'chegg';

// Global variables
let likeCount = ''; 
let dislikeCount = ''; 
let processingMessageRef = null; 

// Helper function to send a processing message
async function sendProcessingMessage(channel) {
  const processingEmbed = new MessageEmbed()
    .setColor('#3498db')
    .setTitle('Processing')
    .setDescription('Your Chegg link is being processed. Please wait...')
    .setFooter({text: 'This may take a few moments'});
  
  try {
    processingMessageRef = await channel.send({ embeds: [processingEmbed] });
    return processingMessageRef;
  } catch (error) {
    console.error('Error sending processing message:', error);
    return null;
  }
}

// Helper function to delete the processing message
function deleteProcessingMessage() {
  if (processingMessageRef) {
    processingMessageRef.delete().catch(err => console.error('Error deleting processing message:', err));
    processingMessageRef = null;
  }
}

// Update cookie handling to support 4 cookies in sequential order
let cookieFiles = [];
let currentCookieIndex = 0; // Track which cookie we're currently using

// Load cookies from files and filter out empty ones
function loadCookies() {
  cookieFiles = [];
  try {
    const cookie1 = fs.readFileSync("cookie1.txt", "utf8").trim();
    if (cookie1) cookieFiles.push({ content: cookie1, index: 1 });
  } catch (error) {
    console.log("cookie1.txt not found or empty");
  }
  
  try {
    const cookie2 = fs.readFileSync("cookie2.txt", "utf8").trim();
    if (cookie2) cookieFiles.push({ content: cookie2, index: 2 });
  } catch (error) {
    console.log("cookie2.txt not found or empty");
  }
  
  try {
    const cookie3 = fs.readFileSync("cookie3.txt", "utf8").trim();
    if (cookie3) cookieFiles.push({ content: cookie3, index: 3 });
  } catch (error) {
    console.log("cookie3.txt not found or empty");
  }
  
  try {
    const cookie4 = fs.readFileSync("cookie4.txt", "utf8").trim();
    if (cookie4) cookieFiles.push({ content: cookie4, index: 4 });
  } catch (error) {
    console.log("cookie4.txt not found or empty");
  }
  
  console.log(`Loaded ${cookieFiles.length} cookies`);
}

// Get the next cookie in the rotation
function getNextCookie() {
  if (cookieFiles.length === 0) {
    console.error("No valid cookies found!");
    return { content: "", index: 0 };
  }
  
  const cookie = cookieFiles[currentCookieIndex];
  // Move to the next cookie for next time, looping back to 0 if needed
  currentCookieIndex = (currentCookieIndex + 1) % cookieFiles.length;
  
  return cookie;
}

// Load cookies at startup
loadCookies();

// Base headers without cookie - we'll add the cookie for each request
const headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
  Accept: "*/*, application/json",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br",
  Referer: "https://www.chegg.com/",
  "content-type": "application/json",
  "apollographql-client-name": "chegg-web",
  "apollographql-client-version": "main-5df873cd-4034069560",
  Authorization: "Basic TnNZS3dJMGxMdVhBQWQwenFTMHFlak5UVXAwb1l1WDY6R09JZVdFRnVvNndRRFZ4Ug==",
  Origin: "https://www.chegg.com",
  Connection: "keep-alive",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-site",
  TE: "trailers",
};

const token = "MTI0NDAzNjIwNzgxNDYzOTc2OQ.Gy5dNa._dbsMtVUGjczXzxKleRJQ6uApftVdHu7j7aTrM";
const channelId = "1240006256278638662";
const prefix = "!";

// Function to get current time in IST
function getCurrentTimeIST() {
  return moment().tz('Asia/Kolkata').format('YYYY-MM-DD HH:mm:ss');
}

// Function to get a random thumbnail URL
function getRandomThumbnailUrl() {
  const gifUrls = [
    'https://cdn.discordapp.com/attachments/1093746006241329252/1186392077790085120/icon.png',
  ];
  const randomIndex = Math.floor(Math.random() * gifUrls.length);
  return gifUrls[randomIndex];
}

// Function to generate a random color
function getRandomColor() {
  const colors = [
    '#0099ff', '#ff9900', '#00ff99', '#9900ff', '#ff0099', '#99ff00',
    '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',
  ];
  const randomIndex = Math.floor(Math.random() * colors.length);
  return colors[randomIndex];
}

// QnA callback handler
function handleQnaCallback(error, response, body, message, url_chegg, cookieInfo) {
  if (!error && response.statusCode == 200) {
    try {
      const jsonData = JSON.parse(body);
      const obj = JSON.parse(body);
      
      console.log(jsonData); // Log the full response for debugging
      
      // Process the real answer data from Chegg
      let authorFirstName,
        authorLastName,
        authorNickname,
        authorAnswerCount,
        legacyId;
      let answerHtml = "";
      let answerHtmll = "";
      
      try {
        if (obj.data.questionByLegacyId.isAutomatedAnswer === true) {
          let answerHtml = obj.data.questionByLegacyId.displayAnswers.bodyMdText;
          let html_with_br = answerHtml.replace(/\n/g, "<br>");
          let answerHtmlu = html_with_br;
          answerHtmll += answerHtmlu;
          console.log(answerHtmll);
        }

        try {
          const ecAnswers = obj.data.questionByLegacyId.displayAnswers.ecAnswers;

          if (ecAnswers && ecAnswers.length > 0) {
            ecAnswers.forEach((ecAnswer, index) => {
              console.log(`Processing EC Answer ${index + 1}`, ecAnswer);

              // Check if answerData exists
              if (ecAnswer.answerData) {
                // Process finalAnswerHtml
                if (ecAnswer.answerData.finalAnswerHtml) {
                  console.log("Processing finalAnswerHtml");
                  const finalAnswerHtml = ecAnswer.answerData.finalAnswerHtml.join(" ");
                  answerHtmll += finalAnswerHtml;
                }

                // Process generalGuidance
                if (ecAnswer.answerData.generalGuidance) {
                  console.log("Processing generalGuidance");
                  const generalGuidanceHtml = ecAnswer.answerData.generalGuidance
                    .map((guide) => guide.html)
                    .join(" ");

                  // Wrap the general guidance in an <h2> tag with red color
                  const redHeadingGeneralGuidance = `<h2 style="color: red;">General Guidance</h2>${generalGuidanceHtml}`;

                  answerHtmll += redHeadingGeneralGuidance;
                }

                // Process steps
                if (ecAnswer.answerData.steps) {
                  console.log("Processing steps");
                  ecAnswer.answerData.steps.forEach((step) => {
                    const stepName = step.name || ""; // Get the step name (if available)
                    const textHtml = step.textHtml || "";
                    const hintsHtml = step.hintsHtml ? step.hintsHtml.join(" ") : "";
                    const answerHtml = step.answerHtml || "";
                    const explanationHtml = step.explanationHtml || "";

                    // Wrap step content in an <h3> heading and include explanation, hints, math, etc.
                    const stepContent = `
                      <h3>${stepName}</h3>
                      <h4>Explanation</h4>
                      ${explanationHtml}
                      <h4>Hints</h4>
                      ${hintsHtml}
                      ${answerHtml}
                      ${textHtml}`;

                    answerHtmll += stepContent;
                  });
                }
              } else {
                console.log(`No answerData found for EC Answer ${index + 1}`);
              }
            });
          } else {
            console.log("No EC Answers found.");
          }
          
          // If we have processed EC answers, use them
          if (answerHtmll) {
            answerHtml = answerHtmll;
          }

          // Try to get HTML answers if EC answers weren't available or complete
          try {
            legacyId = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].legacyId;
            authorFirstName = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].answerData.author.firstName;
            authorLastName = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].answerData.author.lastName;
            authorNickname = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].answerData.author.nickname;
            authorAnswerCount = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].answerData.author.answerCount;
            
            // Only overwrite answerHtml if we didn't get content from EC answers
            if (!answerHtml) {
              answerHtml = obj.data.questionByLegacyId.displayAnswers.htmlAnswers[0].answerData.html;
            }
          } catch (error) {
            // If we didn't get author info above, set them to null
            if (!legacyId) legacyId = null;
            if (!authorFirstName) authorFirstName = null;
            if (!authorLastName) authorLastName = null;
            if (!authorNickname) authorNickname = null;
            if (!authorAnswerCount) authorAnswerCount = null;
            
            // Try SQNA answers format if HTML answers weren't available
            try {
              const objeto = JSON.parse(body);
              const respuesta = objeto.data.questionByLegacyId.displayAnswers.sqnaAnswers.answerData[0].bodyV2.text;
              const objetoo = JSON.parse(respuesta);
              
              // Process the final answer
              const finalAnswerBlocks = objetoo.finalAnswer.blocks;
              let finalAnswerText = "";
              
              // Function to handle text content with styling
              function handleTextContent(contentItems, entityMap) {
                let currentTextStyle = "";
                let contentArray = [];

                contentItems.forEach((textItem) => {
                  if (textItem.type === "text" && textItem.text) {
                    let styledText = textItem.text;
                    if (currentTextStyle.includes("BOLD")) {
                      styledText = `<strong>${styledText}</strong>`;
                    }
                    if (currentTextStyle.includes("ITALIC")) {
                      styledText = `<em>${styledText}</em>`;
                    }
                    contentArray.push(styledText);
                  } else if (textItem.type === "inlineMath" && textItem.content) {
                    const mathText = textItem.content[0]?.text || "";
                    const inlineMathHtml = `<span class="math">\`${mathText}\`</span>`;
                    contentArray.push(inlineMathHtml);
                  } else if (textItem.content) {
                    contentArray.push(...handleTextContent(textItem.content, entityMap));
                  }

                  if (textItem.inlineStyleRanges && textItem.inlineStyleRanges.length) {
                    textItem.inlineStyleRanges.forEach((styleRange) => {
                      if (styleRange.style === "BOLD") {
                        currentTextStyle += "BOLD ";
                      } else if (styleRange.style === "ITALIC") {
                        currentTextStyle += "ITALIC ";
                      }
                    });
                  }
                });

                return contentArray;
              }
              
              // Process the final answer blocks
              finalAnswerBlocks.forEach((block) => {
                if (block.type === "TEXT") {
                  const entityMap = block.block.editorContentState.entityMap || {};
                  const blocks = block.block.editorContentState.content || [];
                  
                  if (blocks.length > 0) {
                    const combinedContent = handleTextContent(blocks, entityMap).join("");
                    finalAnswerText += `<p>${combinedContent}</p>`;
                  } else if (block.block.editorContentState.blocks) {
                    // Handle older format
                    block.block.editorContentState.blocks.forEach(blockItem => {
                      if (blockItem.text) {
                        finalAnswerText += `<p>${blockItem.text}</p>`;
                      }
                    });
                  }
                } else if (block.type === "CHEMISTRY") {
                  // Handle chemistry blocks by adding placeholders
                  finalAnswerText += `<div class="chemistry-block">[Chemistry content]</div>`;
                }
              });
              
              const finalAnswerDiv = `
                <div id="finalAnswer" style="background-color: ; padding: 10px; border: 2px solid #ff69b4;">
                  <h2>Final Answer</h2>
                  ${finalAnswerText}
                </div>
              `;
              
              // Create rectangle box for step names
              function createRectangleBox(stepName) {
                return `<div style="width: 100%;">
                  <div style="border-bottom: 1px solid grey; width: 100%;"></div>
                  <div style="padding: 10px;">${stepName}</div>
                  <div style="border-bottom: 1px solid grey; width: 100%;"></div>
                </div>`;
              }
              
              // Get the steps
              const steps = objetoo.stepByStep.steps;
              
              // Process steps and build HTML
              let stepsHtml = "";
              steps.forEach((step, index) => {
                const stepName = step.name ? step.name : `Step ${index + 1}`;
                const stepNameWithBox = createRectangleBox(stepName);
                stepsHtml += `<h2>${stepNameWithBox}</h2>`;
                
                // Process each block in the step
                step.blocks.forEach((block) => {
                  if (block.type === "TEXT") {
                    const entityMap = block.block.editorContentState.entityMap || {};
                    let contentArray = [];

                    if (block.block.editorContentState.type === "doc") {
                      // Process doc type content
                      function handleDocContent(contentItems) {
                        let currentTextStyle = "";
                        contentItems.forEach((textItem) => {
                          if (textItem.type === "text" && textItem.text) {
                            let styledText = textItem.text;
                            if (currentTextStyle.includes("BOLD")) {
                              styledText = `<strong>${styledText}</strong>`;
                            }
                            if (currentTextStyle.includes("ITALIC")) {
                              styledText = `<em>${styledText}</em>`;
                            }
                            contentArray.push(styledText);
                          } else if (textItem.type === "inlineMath" && textItem.content) {
                            const mathText = textItem.content[0]?.text || "";
                            const inlineMathHtml = `<span class="math">\`${mathText}\`</span>`;
                            contentArray.push(inlineMathHtml);
                          } else if (textItem.content) {
                            handleDocContent(textItem.content);
                          }
                        });
                      }

                      const blocks = block.block.editorContentState.content || [];
                      handleDocContent(blocks);
                      stepsHtml += `<p>${contentArray.join("")}</p>`;
                    } else {
                      // Process blocks type content
                      const blocks = block.block.editorContentState.blocks || [];
                      blocks.forEach((blockItem) => {
                        let entityProcessed = false;

                        // Process entity ranges if present
                        if (blockItem.entityRanges && blockItem.entityRanges.length) {
                          blockItem.entityRanges.forEach((entityRange) => {
                            const entityKey = entityRange.key.toString();
                            const entity = entityMap[entityKey];

                            if (entity && entity.data && entity.data.text) {
                              contentArray.push(`<span class="math">\`${entity.data.text}\`</span><br>`);
                              entityProcessed = true;
                            }
                          });
                        }

                        // If no entities were processed and block has text
                        if (!entityProcessed && blockItem.text) {
                          contentArray.push(blockItem.text);
                        }
                      });

                      stepsHtml += `<p>${contentArray.join("")}</p>`;
                    }
                  } else if (block.type === "MATH_IN_TEXT") {
                    // Handle math expressions
                    if (block.block.expression && block.block.expression.editorContentState) {
                      const mathExpression = block.block.expression.editorContentState.blocks?.[0]?.text || "";
                      const mathResult = block.block.result?.editorContentState?.blocks?.[0]?.text || "";
                      stepsHtml += `<p>Math Expression: <span class="math">\`${mathExpression}\`</span></p>`;
                      if (mathResult) {
                        stepsHtml += `<p>Result: <span class="math">\`${mathResult}\`</span></p>`;
                      }
                    }
                  } else if (block.type === "EQUATION_RENDERER") {
                    // Handle equation renderer
                    if (block.block.lines) {
                      let equationHTML = "<p><strong>Equation:</strong> ";
                      block.block.lines.forEach((line, i) => {
                        equationHTML += `<span class="math">\`${line.left} ${line.operator} ${line.right}\`</span>`;
                        if (i < block.block.lines.length - 1) {
                          equationHTML += " ";
                        }
                      });
                      equationHTML += "</p>";
                      stepsHtml += equationHTML;
                    }
                  } else if (block.type === "EXPLANATION") {
                    // Handle explanations
                    stepsHtml += `<h5 style="color: black;">Explanation</h5>`;
                    const entityMap = block.block.editorContentState.entityMap || {};
                    let contentArray = [];

                    if (block.block.editorContentState.type === "doc") {
                      // Handle doc type explanations
                      function handleExplanationContent(contentItems) {
                        contentItems.forEach((textItem) => {
                          if (textItem.type === "text" && textItem.text) {
                            contentArray.push(textItem.text);
                          } else if (textItem.type === "inlineMath" && textItem.content) {
                            const mathText = textItem.content[0]?.text || "";
                            contentArray.push(`<span class="math">\`${mathText}\`</span>`);
                          } else if (textItem.content) {
                            handleExplanationContent(textItem.content);
                          }
                        });
                      }

                      const blocks = block.block.editorContentState.content || [];
                      handleExplanationContent(blocks);
                    } else {
                      // Handle blocks type explanations
                      const blocks = block.block.editorContentState.blocks || [];
                      blocks.forEach((blockItem) => {
                        if (blockItem.text) {
                          contentArray.push(blockItem.text);
                        }
                      });
                    }

                    stepsHtml += `<p style="text-align: left;">${contentArray.join("")}</p>`;
                  } else if (block.type === "CODE_SNIPPET") {
                    // Handle code snippets
                    if (block.block && block.block.content && block.block.content.content) {
                      const contentArray = block.block.content.content;
                      if (contentArray.length > 0) {
                        const codeContent = contentArray[0];
                        if (codeContent.type === "codeBlock" && codeContent.content && codeContent.content[0]) {
                          const codeText = codeContent.content[0].text;
                          const escapedCode = codeText
                            .replace(/&/g, "&amp;")
                            .replace(/</g, "&lt;")
                            .replace(/>/g, "&gt;");
                          stepsHtml += `<pre class="code-snippet"><code>${escapedCode}</code></pre>`;
                        }
                      }
                    }
                  }
                });
              });
              
              // Combine steps with final answer
              answerHtml = stepsHtml + finalAnswerDiv;
            } catch (error) {
              console.error("Error processing SQNA format:", error);
            }
          }
        } catch (error) {
          console.error("Error processing EC Answers:", error);
        }
      } catch (error) {
        console.error("Error processing answer data:", error);
      }
      
      // Read template and send answer
      fs.readFile('Q&A.html', 'utf-8', async (err, data) => {
        if (err) {
          console.error(err);
          deleteProcessingMessage();
          
          const errorEmbed = new MessageEmbed()
            .setColor('#e74c3c')
            .setTitle('Error')
            .setDescription('Error reading Q&A template file.');
          
          message.channel.send({ embeds: [errorEmbed] });
          return;
        }
        
        // Replace template placeholders with actual content
        let updatedContent = data
          .replace('{{Link}}', url_chegg)
          .replace('{{authorNickname}}', authorNickname || 'Unknown Author')
          .replace('{{answers_wrap}}', answerHtml || 'No answer content found.')
          .replace('{{authorAnswerCount}}', authorAnswerCount || '0');
        
        // Generate unique filename
        const newName = crypto.randomBytes(16).toString('hex');
        
        // Upload to Cloudflare R2
        const params = {
          Bucket: R2_BUCKET_NAME,
          Key: `${R2_FOLDER}/${newName}.html`,
          Body: updatedContent,
          ContentType: "text/html",
        };
        
        s3.putObject(params, (s3Err, data) => {
          if (s3Err) {
            console.error('Error uploading to Cloudflare R2:', s3Err);
            deleteProcessingMessage();
            
            const errorEmbed = new MessageEmbed()
              .setColor('#e74c3c')
              .setTitle('Error')
              .setDescription('Error uploading answer to storage.');
              
            message.channel.send({ embeds: [errorEmbed] });
            return;
          }
          
          // Generate presigned URL for the uploaded HTML
          const urlParams = {
            Bucket: R2_BUCKET_NAME,
            Key: `${R2_FOLDER}/${newName}.html`,
            Expires: 86400,
          };
          
          const presignedUrl = s3.getSignedUrl("getObject", urlParams);
          
          // Delete processing message
          deleteProcessingMessage();
          
          // Create and send embed with answer link
          const embed = new MessageEmbed()
            .setColor(getRandomColor())
            .setTitle('Chegg Q&A Unlocked')
            .setThumbnail(getRandomThumbnailUrl())
            .setAuthor({
              name: message.author.username,
              iconURL: message.author.avatarURL()
            })
            .addField('For', message.author.toString(), true)
            .addField('Question', `[View Question](${url_chegg})`, true)
            .addField('Cookie Used', `Server #${cookieInfo.index}`, true)
            .setFooter({text: 'Study Solutions'});
          
          const row = new MessageActionRow().addComponents(
            new MessageButton()
              .setStyle('LINK')
              .setURL(presignedUrl)
              .setLabel('View Answer')
          );
          
          message.channel.send({
            embeds: [embed],
            components: [row]
          }).catch(console.error);
        });
      });
    } catch (error) {
      console.error("Error processing answer:", error);
      deleteProcessingMessage();
      
      const errorEmbed = new MessageEmbed()
        .setColor('#e74c3c')
        .setTitle('Error')
        .setDescription('Error processing the answer data.');
        
      message.channel.send({ embeds: [errorEmbed] });
    }
  } else {
    console.error("Error fetching Q&A:", error);
    deleteProcessingMessage();
    
    const errorEmbed = new MessageEmbed()
      .setColor('#e74c3c')
      .setTitle('Error')
      .setDescription('Error occurred while fetching the Q&A data.');
      
    message.channel.send({ embeds: [errorEmbed] });
  }
}

// Define the textbook callback handler
function handleTextbookCallback(error, response, body, message, url_chegg, cookieInfo) {
  if (error || response.statusCode !== 200) {
    console.error("Error fetching textbook solution:", error);
    deleteProcessingMessage();
    
    const errorEmbed = new MessageEmbed()
      .setColor('#e74c3c')
      .setTitle('Error')
      .setDescription('Error occurred while fetching the textbook solution.');
      
    message.channel.send({ embeds: [errorEmbed] });
    return;
  }
  
  try {
    // Parse the JSON response
    const jsonData = JSON.parse(body);

    // Extract the solution content from the response
    if (jsonData && jsonData.data && jsonData.data.tbsSolutionContent) {
      const steps = jsonData.data.tbsSolutionContent[0].stepsLink;
      let answerHtml = "";

      // Combine all the HTML from each step
      for (let i = 0; i < steps.length; i++) {
        const html = steps[i].html;
        answerHtml = answerHtml + html;
      }
      
      // Read the template file and replace placeholders
      fs.readFile("TXTBK.html", "utf-8", (err, data) => {
        if (err) {
          console.error(err);
          deleteProcessingMessage();
          
          const errorEmbed = new MessageEmbed()
            .setColor('#e74c3c')
            .setTitle('Error')
            .setDescription('Error reading template file for textbook solution.');
            
          message.channel.send({ embeds: [errorEmbed] });
          return;
        }

        // Replace placeholders in the template
        let updatedContent = data
          .replace("{{Link}}", url_chegg)
          .replace("{{answers_wrap}}", answerHtml);

        // Generate a random file name for the HTML file
        const newName = crypto.randomBytes(16).toString("hex");
        
        // Upload to Cloudflare R2
        const params = {
          Bucket: R2_BUCKET_NAME,
          Key: `${R2_FOLDER}/${newName}.html`,
          Body: updatedContent,
          ContentType: "text/html",
        };

        s3.putObject(params, (s3Err, data) => {
          if (s3Err) {
            console.error('Error uploading to Cloudflare R2:', s3Err);
            deleteProcessingMessage();
            
            const errorEmbed = new MessageEmbed()
              .setColor('#e74c3c')
              .setTitle('Error')
              .setDescription('Error uploading textbook solution to storage.');
              
            message.channel.send({ embeds: [errorEmbed] });
            return;
          }
          
          // Generate a presigned URL with 24-hour expiration
          const urlParams = {
            Bucket: R2_BUCKET_NAME,
            Key: `${R2_FOLDER}/${newName}.html`,
            Expires: 86400, // 24 hours in seconds
          };
          
          const presignedUrl = s3.getSignedUrl("getObject", urlParams);
          
          // Delete the processing message
          deleteProcessingMessage();
          
          // Create and send the embed with the solution link
          const embed = new MessageEmbed()
            .setColor(getRandomColor())
            .setTitle("Chegg Textbook Solution")
            .setThumbnail(getRandomThumbnailUrl())
            .setAuthor({
              name: message.author.username,
              iconURL: message.author.avatarURL(),
            })
            .addField("Current Time (IST)", getCurrentTimeIST())
            .addField("Cookie Used", `Cookie #${cookieInfo.index}`, true)
            .setFooter({text: "TXTbook solution"});

          // Create a button with the solution link
          const row = new MessageActionRow().addComponents(
            new MessageButton()
              .setStyle("LINK")
              .setURL(presignedUrl)
              .setLabel("View Answer")
              .setEmoji("🔗"),
          );

          // Send the message with the embed and button
          message.channel
            .send({
              embeds: [embed],
              components: [row],
            })
            .catch((error) => {
              console.error(error);
            });
        });
      });
    } else {
      console.error("Failed to extract steps from GraphQL response.");
      deleteProcessingMessage();
      
      const errorEmbed = new MessageEmbed()
        .setColor('#e74c3c')
        .setTitle('Error')
        .setDescription('Failed to extract solution content from Chegg.');
        
      message.channel.send({ embeds: [errorEmbed] });
    }
  } catch (error) {
    console.error("Error processing textbook solution:", error);
    deleteProcessingMessage();
    
    const errorEmbed = new MessageEmbed()
      .setColor('#e74c3c')
      .setTitle('Error')
      .setDescription('Error processing response from Chegg.');
      
    message.channel.send({ embeds: [errorEmbed] });
  }
}

client.on("messageCreate", async (message) => {
  if (!channelIds.includes(message.channel.id)) {
    return; // Do nothing if not in the allowed channels
  }
  
  const channelId = message.channel.id;
  const messageText = message.content;
  
  if (messageText.startsWith(prefix)) {
    // Handle commands
    const command = messageText.slice(prefix.length).trim();

    if (command === "hello") {
      message.channel.send("Hello!");
    }
  } else {
    // Check for Chegg links
    const linkRegex = /(https?:\/\/[^\s]+)/g;
    const links = messageText.match(linkRegex);

    if (links) {
      const url_chegg = links[0]; // Capture the link from the message.

      // Check if the URL starts with the Chegg URL pattern for Q&A
      if (url_chegg.startsWith("https://www.chegg.com/homework-help/questions-and-answers/")) {
        console.log("Expert Q&A");
        // Delete the message immediately
        message.delete()
          .then(() => console.log("Message deleted immediately because it contained a Chegg URL"))
          .catch(err => console.error("Error deleting message:", err));

        // Send a processing message
        sendProcessingMessage(message.channel).catch(console.error);

        // Get a fresh cookie for this request
        const cookieInfo = getNextCookie();
        
        const regex = /q(\d+)/;
        const match = url_chegg.match(regex);
        if (match) {
          const numero = match[1];
          const dataString = `{"operationName":"QnaPageAnswerSub","variables":{"id":${numero}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d0ae376e5622d9d80fdf46c37952445a8ce8306d6c8eddeb4f3ab6f30c022f59"}}}`;
          
          const options = {
            url: "https://gateway.chegg.com/one-graph/graphql",
            method: "POST",
            headers: {
              ...headers,
              Cookie: cookieInfo.content
            },
            gzip: true,
            body: dataString,
          };

          request(options, function callback(error, response, body) {
            // Pass the cookie info to the callback
            handleQnaCallback(error, response, body, message, url_chegg, cookieInfo);
          });
        } else {
          deleteProcessingMessage();
          message.channel.send("Could not parse question ID from URL.");
        }
      } 
      // Check if the URL starts with the Chegg URL pattern for textbook solutions
      else if (url_chegg.startsWith("https://www.chegg.com/homework-help/")) {
        console.log("Textbook Solutions");
        
        // Delete the message immediately
        message.delete()
          .then(() => console.log("Message deleted immediately because it contained a Chegg URL"))
          .catch(err => console.error("Error deleting message:", err));
        
        // Send a processing message for textbook solutions
        sendProcessingMessage(message.channel).catch(console.error);
        
        // Get a fresh cookie for this request
        const cookieInfo = getNextCookie();
        
        const options = {
          url: `${url_chegg}`,
          headers: {
            ...headers,
            Cookie: cookieInfo.content
          },
          gzip: true,
        };
        
        request(options, function callback(error, response, body) {
          if (!error && response.statusCode == 200) {
            const regex = /"isbn13":"(\d+)"/;
            const match = body.match(regex);

            const regexx = /"problemId":"(\d+)"/;
            const matchh = body.match(regexx);

            const ean = match ? match[1] : null;
            const problemId = matchh ? matchh[1] : null;

            if (ean && problemId) {
              const dataStringg = `{"operationName":"SolutionContent","variables":{"ean":"${ean}","problemId":"${problemId}"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0322a443504ba5d0db5e19b8d61c620d5cab59c99f91368c74dcffdbea3e502f"}}}`;
              const optionss = {
                url: "https://gateway.chegg.com/one-graph/graphql",
                method: "POST",
                headers: {
                  ...headers,
                  Cookie: cookieInfo.content
                },
                gzip: true,
                body: dataStringg,
              };
              
              request(optionss, function callbackk(callbackError, callbackResponse, callbackBody) {
                handleTextbookCallback(callbackError, callbackResponse, callbackBody, message, url_chegg, cookieInfo);
              });
            } else {
              console.log("Failed to extract ean and problemId from the response.");
              
              // Delete the processing message and show an error
              deleteProcessingMessage();
              
              const errorEmbed = new MessageEmbed()
                .setColor('#e74c3c') // Red color for error
                .setTitle('Error')
                .setDescription('Failed to extract required information from the textbook solution.');
                
              message.channel.send({ embeds: [errorEmbed] });
            }
          } else {
            console.error("Error fetching textbook solution URL:", error);
            
            // Delete the processing message and show an error
            deleteProcessingMessage();
            
            const errorEmbed = new MessageEmbed()
              .setColor('#e74c3c') // Red color for error
              .setTitle('Error')
              .setDescription('Error occurred while accessing the textbook solution URL.');
              
            message.channel.send({ embeds: [errorEmbed] });
          }
        });
      }
    }
  }
});

client.login(token);
