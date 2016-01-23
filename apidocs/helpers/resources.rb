require 'middleman-syntax'

module Resources
  module Helpers

    STATUSES ||= {
      200 => '200 OK',
      201 => '201 Created',
      202 => '202 Accepted',
      204 => '204 No Content',
      205 => '205 Reset Content',
      301 => '301 Moved Permanently',
      302 => '302 Found',
      307 => '307 Temporary Redirect',
      304 => '304 Not Modified',
      401 => '401 Unauthorized',
      403 => '403 Forbidden',
      404 => '404 Not Found',
      405 => '405 Method not allowed',
      409 => '409 Conflict',
      422 => '422 Unprocessable Entity',
      500 => '500 Server Error',
      502 => '502 Bad Gateway'
    }

    def json(key)
      hash = get_resource(key)
      hash = yield hash if block_given?

      Middleman::Syntax::Highlighter.highlight(JSON.pretty_generate(hash), 'json').html_safe
    end

    def get_resource(key)
      hash = case key
        when Hash
          h = {}
          key.each { |k, v| h[k.to_s] = v }
          h
        when Array
          key
        else Resources.const_get(key.to_s.upcase)
      end
      hash
    end

    def text_html(response, status, head = {})
      hs = headers(status, head.merge('Content-Type' => 'text/html'))
      res = CGI.escapeHTML(response)
      hs + %(<pre class="body-response"><code>) + res + "</code></pre>"
    end

  end

  AUTH_TOKEN ||= {
      token: "lkja8*lkajsd*lkjas;ldkj8asd;kJASd811"
  }

  STORE ||= {
      id: 1,
      name: 'Dennys',
      category: 1,
      address: {
          line1: '324 Miracle Way',
          line2: 'Unit 34',
          line3: '',
          zip_code: 90210,
          city: 'Miami',
          state: 'Florida',
          country: 'United States',
          coords: {
              lat: 34,
              long: 45
          }
      },
      photo: {
          url: 'https://google.ca/rawr.png'
      },
      website: 'https://dennys.com',
      tagline: 'Have some yummy in your tummy food',
      distance: nil
  }

  STORE_CATEGORY ||= {
      id: 1,
      name: 'Bars',
      icon: {
          url: 'https://google.ca/rawr.png'
      },
  }

  USER ||= {
      id: 1,
      email: 'john@gmail.com',
      first_name:' John',
      last_name: 'Smith'
  }

end

include Resources::Helpers
